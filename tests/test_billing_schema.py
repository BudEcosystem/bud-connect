"""The billing block: rules a rate must be applied under, and whether to trust it.

``input_cost``/``output_cost`` carry one float per cost field. Metering a voice vendor needs
more than a float -- vendors bill in different units, discount by volume, round up, and impose
minimum charges -- so the float alone understates short requests and overstates committed
volume, in opposite directions.

Two kinds of test here. The schema half imports ``budconnect.model.schemas`` directly, which
is standalone. The seeder half cannot: ``budconnect.seeders.tensorzero`` reaches the ORM and
fails on a circular import, so ``derive_billing`` is read out of the source and executed
against a stub, the same way ``test_voice_providers.py`` reads ``NO_MODEL_PROVIDERS``.
"""

import ast
import pathlib
import re
import types
from typing import Any, Dict, Optional

import pytest
from pydantic import ValidationError

from budconnect.commons.constants import BillingUnitEnum, PriceConfidenceEnum
from budconnect.model.schemas import Billing, BillingSource, BillingTier, LiteLLMModelInfo


REPO_ROOT = pathlib.Path(__file__).parent.parent
SEEDER_PATH = REPO_ROOT / "budconnect" / "seeders" / "tensorzero.py"
MODELS_PATH = REPO_ROOT / "budconnect" / "model" / "models.py"
SCHEMAS_PATH = REPO_ROOT / "budconnect" / "model" / "schemas.py"
MIGRATIONS_DIR = REPO_ROOT / "alembic" / "versions"


# --------------------------------------------------------------------------- #
# the schema
# --------------------------------------------------------------------------- #


def test_an_empty_billing_block_means_unknown_not_free():
    """The whole point of the field.

    ``input_cost`` is nullable, so "nobody could find a price" and "this vendor is free" are
    the same absent value. A consumer that reads the absence as zero bills nothing and says
    nothing about it. Defaulting to UNKNOWN makes the ignorance explicit and greppable.
    """
    assert Billing().confidence is PriceConfidenceEnum.UNKNOWN


def test_unknown_carries_no_rate():
    """UNKNOWN must not ship a number alongside it.

    A rate with UNKNOWN confidence is the worst of both: it looks billable and is not.
    """
    billing = Billing(confidence=PriceConfidenceEnum.UNKNOWN)
    assert billing.tiers is None
    assert billing.unit is None


def test_the_unit_is_recorded_because_the_rate_does_not_imply_it():
    """$0.10 per 1K characters and $0.22 per hour are both one float in `input_cost`."""
    assert Billing(unit="character").unit is BillingUnitEnum.CHARACTER
    assert Billing(unit="second").unit is BillingUnitEnum.SECOND


def test_an_unrecognised_unit_is_rejected():
    """A free-text unit is a unit nobody can multiply by."""
    with pytest.raises(ValidationError):
        Billing(unit="per_fortnight")


def test_an_unrecognised_confidence_is_rejected():
    with pytest.raises(ValidationError):
        Billing(confidence="probably_fine")


def test_billing_forbids_unknown_fields():
    """Same `extra = "forbid"` as every other cost model.

    A typo'd key that silently vanishes is how a rate ends up looking complete and being
    wrong.
    """
    with pytest.raises(ValidationError):
        Billing(minimum_billable_units=15)


@pytest.mark.parametrize("model", [BillingTier, BillingSource])
def test_the_nested_models_forbid_unknown_fields_too(model):
    with pytest.raises(ValidationError):
        model(nonsense=1)


def test_an_unbounded_final_tier_is_expressible():
    """AWS publishes four tiers per SKU; the last has no ceiling."""
    tiers = [
        BillingTier(up_to_units=15_000_000, rate=0.0005),
        BillingTier(up_to_units=None, rate=0.00019),
    ]
    assert tiers[-1].up_to_units is None


def test_a_tier_must_have_a_rate():
    """A threshold with no price is not a tier."""
    with pytest.raises(ValidationError):
        BillingTier(up_to_units=1000)


def test_currency_defaults_to_usd():
    assert Billing().currency == "USD"


def test_a_minimum_and_a_rounding_increment_are_both_expressible():
    """Rev AI: "rounded up to the nearest second, 15 second minimum".

    A 3-second clip costs the same as a 15-second one. Without these two fields the flat
    per-second rate bills 3, and every short request is undercharged.
    """
    billing = Billing(unit="second", min_billable_units=15, rounding_increment=1)
    assert billing.min_billable_units == 15
    assert billing.rounding_increment == 1


def test_provenance_survives_the_round_trip():
    """A curated rate is only safe to bill from while someone can tell how stale it is."""
    billing = Billing(
        confidence=PriceConfidenceEnum.CURATED,
        source=BillingSource(url="https://www.rev.ai/pricing", checked_on="2026-09-22"),
    )
    dumped = billing.model_dump(exclude_none=True)
    assert dumped["source"]["checked_on"] == "2026-09-22"
    assert dumped["confidence"] is PriceConfidenceEnum.CURATED


# --------------------------------------------------------------------------- #
# the wiring
# --------------------------------------------------------------------------- #


def test_the_orm_has_the_column():
    """Read as source: importing the ORM standalone hits a circular import."""
    assert re.search(r"^\s*billing: Mapped\[Dict\[str, Any\]\] = mapped_column\(JSONB", MODELS_PATH.read_text(), re.M)


def test_exactly_one_migration_adds_the_column():
    adders = [p for p in MIGRATIONS_DIR.glob("*.py") if '"billing"' in p.read_text() and "add_column" in p.read_text()]
    assert len(adders) == 1, f"expected one migration adding model_info.billing, found {[p.name for p in adders]}"


def test_the_migration_graph_still_has_a_single_head():
    """Two heads is an `alembic upgrade head` that refuses to run."""
    revisions, parents = {}, set()
    for path in MIGRATIONS_DIR.glob("*.py"):
        text = path.read_text()
        rev = re.search(r"^revision(?::\s*str)?\s*=\s*['\"]([^'\"]+)", text, re.M)
        down = re.search(r"^down_revision(?::\s*[^=]+)?\s*=\s*['\"]([^'\"]+)", text, re.M)
        if rev:
            revisions[rev.group(1)] = path.name
        if down:
            parents.add(down.group(1))
    heads = [r for r in revisions if r not in parents]
    assert len(heads) == 1, f"migration graph has {len(heads)} heads: {[revisions[h] for h in heads]}"


def test_the_response_schema_exposes_billing():
    """budapp cannot apply a rule it is never sent."""
    source = SCHEMAS_PATH.read_text()
    response = source.split("class ModelInfoResponse")[1].split("class ")[0]
    assert "billing:" in response


def test_the_custom_model_dump_strips_nulls_from_billing():
    """`model_dump` special-cases each nested model; one left out ships a dict of Nones."""
    source = SCHEMAS_PATH.read_text()
    nested = source.split("nested_fields = [")[1].split("]")[0]
    assert '"billing"' in nested


# --------------------------------------------------------------------------- #
# derive_billing, executed without importing the seeder
# --------------------------------------------------------------------------- #


def _derive_billing():
    """Pull the static method out of the seeder source and make it callable.

    ``budconnect.seeders.tensorzero`` cannot be imported standalone -- it reaches the ORM and
    raises on a circular import -- and asserting on the AST shape alone would prove the code
    is arranged a certain way, not that it decides correctly.
    """
    tree = ast.parse(SEEDER_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "derive_billing":
            node.decorator_list = []
            module = ast.Module(body=[node], type_ignores=[])
            ast.fix_missing_locations(module)
            namespace = {
                "Billing": Billing,
                "PriceConfidenceEnum": PriceConfidenceEnum,
                "LiteLLMModelInfo": LiteLLMModelInfo,
                "logger": types.SimpleNamespace(warning=lambda *a, **k: None),
                "Dict": Dict,
                "Any": Any,
                "Optional": Optional,
            }
            exec(compile(module, "<derive_billing>", "exec"), namespace)  # noqa: S102
            return namespace["derive_billing"]
    raise AssertionError("derive_billing not found in budconnect/seeders/tensorzero.py")


def _model(config):
    return types.SimpleNamespace(uri="vendor/model", config=config)


def _costs(input_cost=None, output_cost=None):
    return {"input_cost": input_cost or {}, "output_cost": output_cost or {}}


@pytest.mark.asyncio
async def test_an_unpriced_model_is_marked_unknown():
    """The case that matters: ~25 voice vendors have no obtainable per-unit price."""
    result = await _derive_billing()(_model({}), _costs())
    assert result is not None
    assert result.confidence is PriceConfidenceEnum.UNKNOWN


@pytest.mark.asyncio
async def test_a_priced_model_with_nothing_further_to_say_gets_no_block():
    """Existing behaviour is preserved exactly for everything already priced."""
    result = await _derive_billing()(_model({}), _costs(input_cost={"input_cost_per_second": 0.0001}))
    assert result is None


@pytest.mark.asyncio
async def test_a_declared_block_is_carried_through():
    declared = {
        "unit": "second",
        "meter": "input_audio_seconds",
        "min_billable_units": 15,
        "confidence": "curated",
        "source": {"url": "https://www.rev.ai/pricing", "checked_on": "2026-09-22"},
    }
    result = await _derive_billing()(_model({"billing": declared}), _costs(input_cost={"input_cost_per_second": 1}))
    assert result.confidence is PriceConfidenceEnum.CURATED
    assert result.min_billable_units == 15
    assert result.source.url == "https://www.rev.ai/pricing"


@pytest.mark.asyncio
async def test_a_malformed_block_degrades_to_unknown_rather_than_aborting_the_sync():
    """One bad block must not cost every provider its nightly price refresh.

    ``parse_model_data`` already aborts the whole run on an unknown provider; a raise here
    would add a second way for one vendor's data to stop everyone else's prices updating.
    """
    result = await _derive_billing()(_model({"billing": {"unit": "per_fortnight"}}), _costs())
    assert result.confidence is PriceConfidenceEnum.UNKNOWN
