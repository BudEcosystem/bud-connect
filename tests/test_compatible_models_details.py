"""``/model/get-compatible-models?include_details=true`` carries each model's catalog details.

budapp's catalog sync reads this feed, and nothing else it reads says what a model is, so the
"add a cloud model" list has no description until a model is added. The details ride along
only when asked for: budapp and budmodel already call this endpoint without the flag, and their
payload must stay exactly what it was -- the key absent, not ``null``.

The wiring tests read the source: ``budconnect.model.routes`` and ``.services`` pull in the ORM
and cannot be imported standalone.
"""

import ast
import pathlib
from types import SimpleNamespace
from uuid import uuid4

from budconnect.model.schemas import (
    WITHOUT_MODEL_DETAILS,
    CatalogModelDetails,
    CompatibleModelInfo,
    CompatibleModelsResponse,
    CompatibleProviders,
    ModelInfoResponse,
)


MODEL_DIR = pathlib.Path(__file__).parent.parent / "budconnect" / "model"


def _details() -> CatalogModelDetails:
    return CatalogModelDetails(
        description="A model.",
        advantages=["Fast."],
        disadvantages=["Preview."],
        use_cases=["Chat."],
        languages=["English"],
        evaluations=[{"name": "MMLU", "score": 85.9}],
        website_url="https://example.com/model",
    )


def _response(details=None) -> CompatibleModelsResponse:
    model = CompatibleModelInfo(
        id=uuid4(),
        uri="openai/gpt-x",
        modality=["text_input", "text_output"],
        provider_id=uuid4(),
        endpoints=["/v1/chat/completions"],
        billing={"unit": "token"},
        details=details,
    )
    provider = CompatibleProviders(
        id=uuid4(),
        name="OpenAI",
        provider_type="openai",
        icon="icons/providers/openai.png",
        description="OpenAI",
        credentials=[],
        capabilities=["model"],
        models=[model],
    )
    return CompatibleModelsResponse(
        object="model.compatible",
        code=200,
        engine_name="tensorzero",
        engine_version="0.1.0",
        items=[provider],
        total_items=1,
        page=1,
        limit=100,
    )


def _first_model(dumped: dict) -> dict:
    return dumped["items"][0]["models"][0]


def test_without_the_flag_the_key_is_absent_even_when_details_were_attached():
    """Absent, not null: a consumer that never asked must not see a new key."""
    dumped = _response(_details()).model_dump(mode="json", exclude=WITHOUT_MODEL_DETAILS)
    assert "details" not in _first_model(dumped)


def test_without_the_flag_the_model_payload_is_the_old_schema_exactly():
    """What budapp and budmodel receive today: every ModelInfoResponse field, nothing added."""
    dumped = _response().model_dump(mode="json", exclude=WITHOUT_MODEL_DETAILS)
    assert set(_first_model(dumped)) == set(ModelInfoResponse.model_fields)


def test_with_the_flag_the_details_arrive():
    """The fields budapp maps onto a cloud model, next to the catalog fields it already reads."""
    model = _first_model(_response(_details()).model_dump(mode="json"))
    assert model["details"]["description"] == "A model."
    assert model["details"]["advantages"] == ["Fast."]
    assert model["details"]["evaluations"] == [{"name": "MMLU", "score": 85.9}]
    assert model["billing"] == {"unit": "token"}, "the catalog fields must survive alongside details"


def test_a_model_without_details_row_reports_null_when_asked():
    """Asked for, but nothing researched: an explicit null, so budapp can tell the cases apart."""
    assert _first_model(_response(None).model_dump(mode="json"))["details"] is None


def test_null_lists_become_empty_lists():
    """A details row with NULL list columns must not reach budapp as null."""
    row = SimpleNamespace(
        description="A model.",
        advantages=None,
        disadvantages=None,
        use_cases=None,
        languages=None,
        evaluations=None,
        website_url=None,
        github_url=None,
    )
    details = CatalogModelDetails.model_validate(row)
    assert (details.advantages, details.disadvantages, details.use_cases, details.languages) == ([], [], [], [])
    assert details.evaluations == []


def test_a_malformed_evaluation_is_dropped_not_fatal():
    """One bad row must not fail the page: budmodel's Hugging Face path writes this table too."""
    details = CatalogModelDetails.model_validate(
        {
            "evaluations": [
                {"name": "MMLU", "score": 85.9, "source": "https://example.com"},
                {"name": "vibes", "score": "high"},
                {"score": 90},
                {"name": "flag", "score": True},
                "not a dict",
            ]
        }
    )
    assert [(e.name, e.score) for e in details.evaluations] == [("MMLU", 85.9)]


def _function(path: pathlib.Path, name: str) -> ast.AST:
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"{name} not found in {path.name}")


def test_the_route_passes_the_flag_and_drops_the_key_when_it_is_off():
    """A flag the route accepts but never forwards, or a key it never drops, reads as working."""
    source = ast.unparse(_function(MODEL_DIR / "routes.py", "get_compatible_models"))
    assert "include_details" in source.split("ModelService.get_compatible_models(", 1)[1].split(")", 1)[0]
    assert "WITHOUT_MODEL_DETAILS" in source


def test_both_paths_of_the_service_attach_details():
    """No engine returns every provider; an engine returns its compatible ones. Both must carry details."""
    service = _function(MODEL_DIR / "services.py", "get_compatible_models")
    attaches = [
        node
        for node in ast.walk(service)
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "ModelService._attach_details"
    ]
    assert len(attaches) == 2, f"expected an attach on each successful return, found {len(attaches)}"
    guarded = [
        node for node in ast.walk(service) if isinstance(node, ast.If) and ast.unparse(node.test) == "include_details"
    ]
    assert len(guarded) == 2, "details must be attached only when the caller asks for them"


def test_details_are_fetched_in_one_query_per_page():
    """A lazy ``model.details`` per model is ~1,500 queries for one page of the catalog."""
    attach = ast.unparse(_function(MODEL_DIR / "services.py", "_attach_details"))
    assert "get_by_model_info_ids" in attach
    lookup = ast.unparse(_function(MODEL_DIR / "crud.py", "get_by_model_info_ids"))
    assert ".in_(" in lookup
