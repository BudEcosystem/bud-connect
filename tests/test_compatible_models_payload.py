"""The hand-built model payloads in ``ModelService.get_compatible_models``.

``/model/get-compatible-models`` is how budapp learns what bud-connect knows. The service
does not hand the ORM object to Pydantic; it copies fields into a dict literal, four times
over, and passes that to ``ModelInfoResponse``. Anything not on the list arrives at budapp
as ``null`` -- the column is populated, the response schema declares the field, and the
value is silently dropped in between.

That is how ``billing`` shipped broken the first time: migration applied, seeder wrote 28
billing blocks, and every model in the API response had ``billing: null``. Found by running
it, not by reading it, because nothing about the code looks wrong.

These tests read the source rather than calling the service: ``budconnect.model.services``
reaches the ORM and cannot be imported standalone.
"""

import ast
import pathlib

import pytest

from budconnect.model.schemas import ModelInfoResponse


SERVICES_PATH = pathlib.Path(__file__).parent.parent / "budconnect" / "model" / "services.py"

#: Fields carried as JSONB on ``model_info``. Every one of them is a payload the consumer
#: has to receive to price or place a model, and every one is droppable by omission.
JSONB_PAYLOAD = frozenset(
    {
        "input_cost",
        "output_cost",
        "cache_cost",
        "search_context_cost_per_query",
        "tokens",
        "rate_limits",
        "media_limits",
        "features",
        "billing",
    }
)


def _model_data_dicts():
    """Every dict literal in services.py that is built from ``db_model`` attributes."""
    tree = ast.parse(SERVICES_PATH.read_text())
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = {k.value for k in node.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        if "uri" in keys and "provider_id" in keys:
            found.append(keys)
    return found


def test_the_payload_is_built_in_more_than_one_place():
    """If this ever drops to one, delete this file and the duplication it guards."""
    dicts = _model_data_dicts()
    assert len(dicts) >= 2, f"expected several hand-built payloads, found {len(dicts)}"


#: Keys that come from a JOIN rather than from the model row, so their presence varies
#: legitimately by endpoint.
JOIN_DERIVED = frozenset({"provider_name", "provider_type", "license", "architecture_class"})

#: Drift that already existed before ``billing`` was added, recorded rather than asserted
#: away: the detail/search payloads carry timestamps and omit ``status``; the
#: compatible-models payloads do the reverse. Both are real inconsistencies in what the API
#: reports, and worth fixing -- but fixing them changes responses budapp already consumes,
#: so it is a separate change. Listing them here means NEW drift fails this test while the
#: known drift does not.
KNOWN_DRIFT = frozenset({"created_at", "modified_at", "status"})


def test_no_new_drift_between_the_hand_built_payloads():
    """Six copies of one payload drift, and the drift is invisible in review.

    A field added to five of the six produces a response that is correct on some endpoints
    and null on others, depending on which one served the request.
    """
    shapes = {frozenset(keys - JOIN_DERIVED) for keys in _model_data_dicts()}
    differences: set = set()
    for shape in shapes:
        for other in shapes:
            differences |= shape ^ other

    unexpected = differences - KNOWN_DRIFT
    assert not unexpected, (
        f"payloads have started to disagree on {sorted(unexpected)}; a field present in some "
        "payloads and absent from others reaches budapp as null on whichever endpoints omit it"
    )


@pytest.mark.parametrize("field", sorted(JSONB_PAYLOAD))
def test_every_jsonb_payload_field_is_copied(field):
    """The specific failure: a populated column that arrives as null."""
    for i, keys in enumerate(_model_data_dicts()):
        assert field in keys, (
            f"{field!r} is missing from hand-built payload #{i} in services.py, so it will "
            f"reach budapp as null however well it is populated"
        )


def test_the_response_schema_declares_everything_the_payload_sends():
    """The other direction: a key copied into a dict that the schema would reject."""
    declared = set(ModelInfoResponse.model_fields)
    for i, keys in enumerate(_model_data_dicts()):
        unknown = keys - declared
        assert not unknown, f"payload #{i} sends {sorted(unknown)}, which ModelInfoResponse does not declare"


CRUD_PATH = SERVICES_PATH.parent / "crud.py"


def _cost_bearing_dicts():
    """Every dict literal in the model services AND crud that copies a model's prices.

    Wider than ``_model_data_dicts``: the two model-DETAILS payloads (the CRUD join and the
    service's by-id path) key on ``provider_name``, not ``provider_id``, so the check above
    never saw them -- and both dropped ``billing`` while every list endpoint carried it.
    """
    found = []
    for path in (SERVICES_PATH, CRUD_PATH):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Dict):
                continue
            keys = {k.value for k in node.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            if "uri" in keys and "input_cost" in keys:
                found.append((path.name, node.lineno, keys))
    return found


def test_the_details_payloads_are_found():
    """If the scan stops finding a file's payloads, the checks below are vacuous."""
    names = {name for name, _, _ in _cost_bearing_dicts()}
    assert names == {"services.py", "crud.py"}, names


@pytest.mark.parametrize("field", sorted(JSONB_PAYLOAD))
def test_every_payload_that_copies_prices_copies_every_jsonb_field(field):
    """Both details payloads dropped `billing` while every list endpoint carried it."""
    for name, line, keys in _cost_bearing_dicts():
        assert field in keys, f"{name}:{line} copies prices but not {field!r}"


@pytest.mark.parametrize("field", sorted(JSONB_PAYLOAD))
def test_the_details_response_declares_every_jsonb_field(field):
    """A key the schema does not declare is dropped by pydantic without a word."""
    from budconnect.model.schemas import ModelDetailsResponse

    assert field in ModelDetailsResponse.model_fields
