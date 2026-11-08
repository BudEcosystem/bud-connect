"""Which catalog models are served at ``/v1/decisions`` (bud-runtime spec 031, CONTRACTS C7).

A decision model answers typed questions (predicate, choice, score) with calibrated probabilities.
Bud serves it on two routes -- ``/v1/decisions`` (OpenAI's shape) and ``/v1/systemone`` (the System
One shape most vendors speak) -- and budapp publishes a deployment carrying ``/v1/decisions`` with a
``system_one`` entry whose URL comes from the provider's ``decisions_url`` credential field, or from
that field's catalog ``default``. So the catalog owns three promises, each tested here:

* the PROVIDER can serve it (TC-CAT-06, TC-CAT-18): the route survives only under a provider that
  declares ``decisions``, and every such provider that is not decisions-native (OpenAI, Azure) carries
  a ``decisions_url`` field -- with the vendor's URL as its default, except the generic
  ``system_one_compatible`` entry, where the user must supply it;
* the MODEL is one (C7.3): ``/v1/decisions`` comes from an explicit endpoint list, never from a mode
  or a modality. LiteLLM files decision models under two modes, ``decisions`` and ``evaluation``;
* it is PRICED and LIMITED (C7.2, FRD D-24, D-25): per token, or per request for Embedding Studio,
  with ``decision_limits`` the gateway enforces before calling the vendor.

The LiteLLM entries below are copied from ``model_prices_and_context_window.json`` as fetched on
2026-11-08 (the fields that decide routes and prices). The verified vendor values come from the live
spike (bud-runtime ``services/budgateway/tensorzero-internal/tests/fixtures/decisions/SPIKE.md``).

Loads the seeder module with its package stubbed out, like ``test_realtime_catalog``.
"""

import asyncio
import importlib
import json
import logging
import os
import re
import sys
import types
import uuid
from pathlib import Path

import pytest
from pydantic import ValidationError

from budconnect.commons.constants import ModalityEnum as M
from budconnect.commons.constants import ModelEndpointEnum as E
from budconnect.commons.constants import PriceConfidenceEnum
from budconnect.commons.constants import ProviderCapabilityEnum as C
from budconnect.commons.exceptions import SeederException
from budconnect.model.schemas import DecisionLimits, LiteLLMModelInfo, ModelInfoCreate, ModelInfoResponse


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_JSON_PATH = REPO_ROOT / "budconnect" / "seeders" / "data" / "tensorzero" / "tensorzero_providers.json"
DECISION_MODELS_PATH = REPO_ROOT / "budconnect" / "seeders" / "data" / "decisions" / "decision_models.json"
CONSTANTS_PATH = REPO_ROOT / "budconnect" / "seeders" / "constants.py"
MIGRATIONS_DIR = REPO_ROOT / "alembic" / "versions"

#: Decisions-native providers: budgateway calls their own ``/v1/decisions`` (CONTRACTS C4), so they
#: carry no ``decisions_url`` field.
NATIVE = {"openai", "azure"}

#: C7.1: every System One vendor and its default URL. ``embedding_space`` is not System One (C3.7) but
#: is published the same way, with its own adapter. ``system_one_compatible`` has no default.
DECISIONS_URL_DEFAULTS = {
    "typesafe": "https://api.typesafe.ai/v1/systemone",
    "perplexity": "https://api.perplexity.ai/v1/decisions",
    "liquid_ai": "https://api.liquid.ai/decisions/v1/systemone",
    "bespokelabs": "https://api.bespokelabs.ai/v1/systemone",
    "subq": "https://api.subq.ai/v1/systemone",
    "fireworks_ai": "https://api.fireworks.ai/inference/v1/systemone",
    "baseten": "https://inference.baseten.co/v1/systemone",
    "embedding_space": "https://api.embedding.in/v1/decide",
}
GENERIC = "system_one_compatible"
DECISIONS_PROVIDERS = NATIVE | set(DECISIONS_URL_DEFAULTS) | {GENERIC}

#: C7.2: the only keys ``decision_limits`` may carry.
LIMIT_KEYS = {"max_questions", "max_choices", "max_levels", "images"}

#: Live-verified on 2026-11-08 (SPIKE.md). Azure shares OpenAI's wire but was not called.
VERIFIED = {
    "openai/gpt-6-luna",
    "typesafe/jev-latest",
    "typesafe/jev-1.14.0",
    "typesafe/jev-1.13.0",
    "embedding_space/laya",
}


# ---- LiteLLM entries, as fetched 2026-11-08 ------------------------------------------------------ #

#: gpt-6-luna: chat, responses AND decisions, the only OpenAI decision model (SPIKE.md).
LITELLM_GPT_6_LUNA = {
    "litellm_provider": "openai",
    "mode": "chat",
    "supported_endpoints": ["/v1/chat/completions", "/v1/batch", "/v1/responses", "/v1/decisions"],
    "supported_modalities": ["text", "image"],
    "supported_output_modalities": ["text"],
    "input_cost_per_token": 1e-07,
    "input_cost_per_token_decisions": 1e-07,
    "output_cost_per_token": 5e-07,
    "output_cost_per_token_decisions": 0.0,
    "cache_read_input_token_cost": 1e-08,
    "max_input_tokens": 922000,
    "max_output_tokens": 128000,
}

#: Azure's gpt-6-luna is listed at chat and responses only.
LITELLM_AZURE_GPT_6_LUNA = {
    "litellm_provider": "azure",
    "mode": "chat",
    "supported_endpoints": ["/v1/chat/completions", "/v1/responses"],
    "input_cost_per_token": 1e-07,
    "output_cost_per_token": 5e-07,
    "cache_read_input_token_cost": 1e-08,
    "max_input_tokens": 922000,
}

#: gpt-5.6-luna is NOT a decision model: OpenAI answers /v1/decisions with 404 (SPIKE.md).
LITELLM_GPT_5_6_LUNA = {
    "litellm_provider": "openai",
    "mode": "chat",
    "supported_endpoints": ["/v1/chat/completions", "/v1/batch", "/v1/responses"],
    "input_cost_per_token": 2e-07,
    "output_cost_per_token": 1.2e-06,
}

#: The two LiteLLM modes decision models are filed under, with no endpoint list.
LITELLM_FIREWORKS_RUNE = {
    "litellm_provider": "fireworks_ai-embedding-models",
    "mode": "decisions",
    "input_cost_per_token": 4.2e-08,
    "output_cost_per_token": 0.0,
    "max_input_tokens": 262144,
}
LITELLM_TYPESAFE_JEV = {
    "litellm_provider": "typesafe",
    "mode": "evaluation",
    "input_cost_per_token": 4.2e-08,
    "output_cost_per_token": 0.0,
    "max_input_tokens": 65536,
}

#: A model a vendor serves on the System One route only: the same capability under its other name.
LITELLM_SYSTEMONE_ONLY = {
    "litellm_provider": "typesafe",
    "mode": "evaluation",
    "supported_endpoints": ["/v1/systemone"],
    "input_cost_per_token": 4.2e-08,
    "output_cost_per_token": 0.0,
}


# ---- helpers ------------------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def tz():
    """Load the real seeder module without its package's import side effects."""
    saved = {k: sys.modules.get(k) for k in ("budconnect.seeders", "budconnect.seeders.tensorzero")}
    import budconnect

    pkg = types.ModuleType("budconnect.seeders")
    pkg.__path__ = [str(Path(budconnect.__file__).parent / "seeders")]
    sys.modules["budconnect.seeders"] = pkg
    sys.modules.pop("budconnect.seeders.tensorzero", None)
    try:
        yield importlib.import_module("budconnect.seeders.tensorzero")
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def _model_info(tz, uri, config, provider_type):
    """Run one entry through the seeder's whole derivation: routes, modalities, gates, prices."""
    config = {k: v for k, v in config.items() if k != "litellm_provider"}
    return asyncio.run(
        tz.TensorZeroParser().create_model_info(
            LiteLLMModelInfo(uri=uri, config=config), uuid.uuid4(), provider_type, None
        )
    )


def _routes(tz, uri, config):
    """Return the routes an entry derives, before any provider gate."""
    config = {k: v for k, v in config.items() if k != "litellm_provider"}
    return asyncio.run(tz.TensorZeroParser.derive_model_specs(LiteLLMModelInfo(uri=uri, config=config)))["endpoints"]


def _providers():
    """Load the provider catalog as shipped."""
    with PROVIDERS_JSON_PATH.open() as handle:
        return json.load(handle)


def _seed():
    """Load the curated decision models as shipped."""
    with DECISION_MODELS_PATH.open() as handle:
        return json.load(handle)


def _seed_by_uri():
    """Load the curated decision models, by uri."""
    return {entry["uri"]: entry for entry in _seed()}


def _credentials(provider):
    """One provider's credential fields, by field name."""
    return {f["field"]: f for f in _providers()[provider]["credentials"]}


def _fake_sdk(monkeypatch, models):
    """Stand in for the catalog SDK, returning `models` as a successful fetch."""

    class Result:
        def __init__(self):
            self.models = models
            self.ai_models_fetched_at = "2026-11-08"
            self.stats = types.SimpleNamespace(matched=0, unmatched=0)

    class CatalogClient:
        def fetch_catalog_sync(self):
            return Result()

    monkeypatch.setitem(sys.modules, "bud_model_catalog", types.SimpleNamespace(CatalogClient=CatalogClient))


def _seed_snapshot(tz, monkeypatch, models):
    """parse_model_data over a fake SDK catalog, then create_model_info for every model: uri -> info."""
    _fake_sdk(monkeypatch, {uri: dict(config) for uri, config in models.items()})
    parsed = asyncio.run(tz.TensorZeroParser.parse_model_data())
    parser = tz.TensorZeroParser()
    return {
        m.uri: asyncio.run(parser.create_model_info(m, uuid.uuid4(), provider, None))
        for provider, ms in parsed.items()
        for m in ms
    }


def _migration_labels(enum_name):
    """Labels every migration adds to a PG enum through `ALTER TYPE ... ADD VALUE`, by file."""
    pattern = re.compile(rf"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '([A-Z_]+)'")
    found = {}
    for path in MIGRATIONS_DIR.glob("*.py"):
        for label in pattern.findall(path.read_text()):
            found.setdefault(label, []).append(path.name)
    return found


# ---- C6/C7 vocabulary ---------------------------------------------------------------------------- #


def test_the_route_and_capability_carry_the_contract_values():
    """Budapp matches these strings exactly; its sync drops or refuses anything else."""
    assert E.DECISIONS.value == "/v1/decisions"
    assert C.DECISIONS.value == "decisions"


@pytest.mark.parametrize(
    ("column", "member", "pg_type"),
    [("endpoints", E.DECISIONS, "modelendpointenum"), ("capabilities", C.DECISIONS, "providercapabilityenum")],
)
def test_one_migration_adds_the_label_the_orm_writes(column, member, pg_type):
    """The columns store member NAMES (no `values_callable`), so the PG label is the name.

    Without it the first seed carrying the value fails its INSERT with "invalid input value for enum".
    """
    from budconnect.model.models import ModelInfo, Provider

    table = ModelInfo if column == "endpoints" else Provider
    assert member.name in table.__table__.c[column].type.item_type.enums, f"the ORM would not write {member.name}"
    assert len(_migration_labels(pg_type).get(member.name, [])) == 1, (
        f"exactly one migration must add {member.name!r} to {pg_type}"
    )


def test_the_orm_and_one_migration_carry_decision_limits():
    """Budapp persists the limits from the feed (TC-CAT-14, TC-CAT-15); the column has to exist."""
    from budconnect.model.models import ModelInfo

    assert "decision_limits" in ModelInfo.__table__.c
    assert ModelInfo.__table__.c["decision_limits"].nullable
    adders = [
        p.name
        for p in MIGRATIONS_DIR.glob("*.py")
        if '"decision_limits"' in p.read_text() and "add_column" in p.read_text()
    ]
    assert len(adders) == 1, f"expected one migration adding model_info.decision_limits, found {adders}"


def test_the_decision_limits_migration_is_reversible():
    """Additive and nullable (fix-forward): the previous image never names the column."""
    path = next(p for p in MIGRATIONS_DIR.glob("*.py") if '"decision_limits"' in p.read_text())
    text = path.read_text()
    assert "nullable=True" in text
    assert re.search(r"def downgrade\(\) -> None:\s+(?:\"\"\".*?\"\"\"\s+)?op\.drop_column", text, re.S)


def test_the_response_schema_sends_decision_limits():
    """A field the response schema does not declare is dropped by pydantic without a word."""
    assert "decision_limits" in ModelInfoResponse.model_fields


# ---- DecisionLimits schema (C7.2) ---------------------------------------------------------------- #


def test_decision_limits_accept_the_contract_keys():
    """The four C7.2 keys round-trip unchanged."""
    limits = DecisionLimits(max_questions=400, max_choices=128, max_levels=10, images=False)
    assert limits.model_dump(exclude_none=True) == {
        "max_questions": 400,
        "max_choices": 128,
        "max_levels": 10,
        "images": False,
    }


def test_decision_limits_are_all_optional():
    """An absent field means "no limit beyond OpenAI's" (C1.4)."""
    assert DecisionLimits().model_dump(exclude_none=True) == {}


@pytest.mark.parametrize(
    "bad",
    [
        {"max_question": 10},  # a typo would otherwise be a limit nobody enforces
        {"max_choices": 0},
        {"max_levels": -1},
        {"max_questions": True},  # a bool is not a count
        {"images": "no"},
        {"max_choices": 2.5},
    ],
)
def test_decision_limits_refuse_what_the_gateway_cannot_enforce(bad):
    """A misspelt key, a non-positive count or a wrong type is refused."""
    with pytest.raises(ValidationError):
        DecisionLimits(**bad)


def test_the_custom_model_dump_strips_nulls_from_decision_limits():
    """`model_dump` special-cases each nested model; one left out ships a dict of Nones."""
    info = ModelInfoCreate(
        uri="typesafe/jev-latest",
        modality=[M.TEXT_INPUT, M.TEXT_OUTPUT],
        provider_id=uuid.uuid4(),
        endpoints=[E.DECISIONS],
        decision_limits=DecisionLimits(max_choices=255),
    )
    assert info.model_dump()["decision_limits"] == {"max_choices": 255}
    empty = ModelInfoCreate(
        uri="x/y", modality=[], provider_id=uuid.uuid4(), endpoints=[], decision_limits=DecisionLimits()
    )
    assert empty.model_dump()["decision_limits"] is None


# ---- C7.3: the route comes from an explicit endpoint list only ------------------------------------ #


def test_an_explicit_decisions_listing_derives_the_route(tz):
    """gpt-6-luna is listed at chat, responses, batch and decisions; every route is kept."""
    assert _routes(tz, "openai/gpt-6-luna", LITELLM_GPT_6_LUNA) == [E.BATCH, E.CHAT, E.DECISIONS, E.RESPONSE]


def test_a_chat_model_without_the_listing_gets_no_decisions_route(tz):
    """gpt-5.6-luna shares the name and not the capability: OpenAI 404s it on /v1/decisions."""
    assert E.DECISIONS not in _routes(tz, "openai/gpt-5.6-luna", LITELLM_GPT_5_6_LUNA)


@pytest.mark.parametrize(
    ("uri", "config"),
    [
        ("fireworks_ai-embedding-models/fireworks_ai/accounts/fireworks/models/rune", LITELLM_FIREWORKS_RUNE),
        ("typesafe/jev-latest", LITELLM_TYPESAFE_JEV),
    ],
)
def test_a_decisions_or_evaluation_mode_alone_grants_nothing(tz, uri, config):
    """LiteLLM files decision models under `decisions` (4 rows) and `evaluation` (35 rows).

    Neither mode is a route: `evaluation` does not even say decisions. The explicit list decides.
    """
    assert _routes(tz, uri, config) == []


def test_the_system_one_listing_is_the_decisions_capability(tz):
    """`/v1/systemone` is the other route of the same capability; Bud serves both for a decisions model."""
    assert _routes(tz, "typesafe/jev-preview", LITELLM_SYSTEMONE_ONLY) == [E.DECISIONS]


def test_a_text_modality_never_implies_decisions(tz):
    """C7.3: never from modality. A text-in/text-out entry with no list gets its mode's routes only."""
    assert E.DECISIONS not in _routes(tz, "openai/x", {"mode": "chat", "supported_modalities": ["text"]})


# ---- TC-CAT-18: the gate ------------------------------------------------------------------------ #


def test_tc_cat_18_the_gate_removes_only_the_decisions_route_and_says_so(tz, caplog):
    """Under a provider without `decisions` the route goes, with one warning naming the model."""
    with caplog.at_level(logging.WARNING, logger=tz.logger.name):
        kept = tz.gate_decisions_route([E.CHAT, E.DECISIONS], [C.MODEL], "vendor/some-model")
    assert kept == [E.CHAT]
    messages = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert len(messages) == 1
    assert "vendor/some-model" in messages[0] and "decisions" in messages[0]


def test_the_gate_keeps_the_route_for_a_provider_that_declares_it(tz, caplog):
    """A provider declaring `decisions` keeps the route, silently."""
    with caplog.at_level(logging.WARNING, logger=tz.logger.name):
        assert tz.gate_decisions_route([E.DECISIONS], [C.MODEL, C.DECISIONS], "typesafe/jev-latest") == [E.DECISIONS]
    assert not caplog.records


def test_the_gate_is_silent_for_a_model_with_no_decisions_route(tz, caplog):
    """A warning on every chat model of every provider would bury the one that matters."""
    with caplog.at_level(logging.WARNING, logger=tz.logger.name):
        assert tz.gate_decisions_route([E.CHAT], [C.MODEL], "anthropic/claude") == [E.CHAT]
    assert not caplog.records


def test_the_gate_applies_through_the_provider_catalog(tz, monkeypatch):
    """create_model_info reads capabilities from the provider catalog; the limits go with the route."""
    monkeypatch.setattr(tz, "_PROVIDER_CAPABILITIES", {"openai": ["model"]})
    config = {**LITELLM_GPT_6_LUNA, "decision_limits": {"max_questions": 400}}
    mi = _model_info(tz, "openai/gpt-6-luna", config, "openai")
    assert E.DECISIONS not in mi.endpoints
    assert E.CHAT in mi.endpoints
    assert mi.decision_limits is None


def test_tc_cat_18_one_sync_logs_a_gated_model_once(tz, monkeypatch, caplog):
    """A provider that lists a model at /v1/decisions without the capability: dropped, logged once."""
    monkeypatch.setattr(tz, "_PROVIDER_CAPABILITIES", None)
    vendor_model = {**LITELLM_GPT_6_LUNA, "litellm_provider": "together_ai"}
    with caplog.at_level(logging.WARNING, logger=tz.logger.name):
        infos = _seed_snapshot(tz, monkeypatch, {"together_ai/gpt-6-luna-clone": vendor_model})
    assert E.DECISIONS not in infos["together_ai/gpt-6-luna-clone"].endpoints
    gated = [r for r in caplog.records if "together_ai/gpt-6-luna-clone" in r.getMessage()]
    assert len(gated) == 1, [r.getMessage() for r in caplog.records]


# ---- TC-CAT-06: providers ------------------------------------------------------------------------ #


def test_tc_cat_06_exactly_the_contract_providers_declare_decisions():
    """The capability puts a provider in the decisions picker; only C7.1's providers may carry it."""
    declaring = {p for p, entry in _providers().items() if "decisions" in entry["capabilities"]}
    assert declaring == DECISIONS_PROVIDERS


@pytest.mark.parametrize("provider", sorted(DECISIONS_PROVIDERS))
def test_a_decisions_provider_still_declares_model(provider):
    """/model/get-compatible-models only returns providers carrying MODEL."""
    assert "model" in _providers()[provider]["capabilities"]


@pytest.mark.parametrize("provider", sorted(DECISIONS_PROVIDERS - NATIVE))
def test_tc_cat_06_every_non_native_decisions_provider_has_a_decisions_url(provider):
    """Budapp publishes `url` from this field or its default (C6); without it there is no URL, only a 400."""
    field = _credentials(provider).get("decisions_url")
    assert field is not None, f"{provider} declares decisions but has no decisions_url credential field"
    assert field["type"] == "url"
    assert field["label"] and isinstance(field["order"], int)


@pytest.mark.parametrize(("provider", "default"), sorted(DECISIONS_URL_DEFAULTS.items()))
def test_a_vendor_url_is_a_default_the_user_may_override(provider, default):
    """C7.1: the vendor URL ships with the catalog, so deploying needs only an API key."""
    field = _credentials(provider)["decisions_url"]
    assert field["default"] == default
    assert field["required"] is False
    assert default.startswith("https://")


@pytest.mark.parametrize("provider", sorted(DECISIONS_URL_DEFAULTS))
def test_a_vendor_requires_an_api_key_and_masks_it(provider):
    """Embedding Studio sends it as X-API-Key, the rest as a bearer token; the field is `api_key` either way."""
    field = _credentials(provider)["api_key"]
    assert field["required"] is True
    assert field["type"] == "password"


def test_the_generic_entry_needs_a_url_and_no_key():
    """FRD D-22: any System One server is one URL and, maybe, a key."""
    creds = _credentials(GENERIC)
    assert creds["decisions_url"]["required"] is True
    assert "default" not in creds["decisions_url"], "a generic entry has no vendor to default to"
    assert creds["api_key"]["required"] is False
    assert creds["api_key"]["type"] == "password"


@pytest.mark.parametrize("provider", sorted(NATIVE))
def test_a_native_provider_carries_no_decisions_url(provider):
    """Budgateway calls OpenAI's and Azure's own /v1/decisions; a URL field would be a setting nothing reads."""
    assert "decisions_url" not in _credentials(provider)


@pytest.mark.parametrize("provider", sorted(DECISIONS_PROVIDERS))
def test_a_decisions_provider_form_is_renderable(provider):
    """The credentials array is the form budadmin renders; every field needs its keys and an order."""
    creds = _providers()[provider]["credentials"]
    for field in creds:
        for key in ("field", "label", "type", "required", "order"):
            assert key in field, f"{provider} credential {field.get('field')!r} is missing {key!r}"
        assert field["type"] in {"password", "url", "string", "text", "textarea"}
    orders = [f["order"] for f in creds]
    assert len(set(orders)) == len(orders)


def test_the_generic_entry_is_seeded_although_it_has_no_models():
    """Its models are the user's own, so only NO_MODEL_PROVIDERS ever reaches it."""
    assert GENERIC in CONSTANTS_PATH.read_text().split("NO_MODEL_PROVIDERS = [")[1].split("]")[0]


@pytest.mark.parametrize("provider", sorted(DECISIONS_PROVIDERS))
def test_every_decisions_provider_has_an_icon_path(provider):
    """Each icon is a PNG under icons/providers/, which budapp resolves in its static directory."""
    icon = _providers()[provider]["icon"]
    assert icon.startswith("icons/providers/") and icon.endswith(".png")


def _bud_runtime_root():
    """Find a bud-runtime checkout to look for budapp's static icons in, or None."""
    env_value = os.environ.get("BUD_RUNTIME_ROOT")
    if env_value:
        return Path(env_value).expanduser()
    for parent in (REPO_ROOT.parent, REPO_ROOT.parent.parent, Path.home()):
        candidate = parent / "bud-runtime"
        if (candidate / "services" / "budapp" / "static").is_dir():
            return candidate
    return None


@pytest.mark.parametrize("provider", sorted(DECISIONS_PROVIDERS))
def test_the_icon_exists_in_budapps_static_files(provider):
    """Budapp serves `icon` from its static directory; a missing file is a broken image in the picker."""
    root = _bud_runtime_root()
    if root is None:
        pytest.skip("ICON CHECK NOT RUN: no bud-runtime checkout found; set BUD_RUNTIME_ROOT to enable it")
    icon = root / "services" / "budapp" / "static" / _providers()[provider]["icon"]
    assert icon.is_file(), f"{provider}'s icon {icon} does not exist"


# ---- C7.2: the curated seed ---------------------------------------------------------------------- #


REQUIRED_SEED_KEYS = {
    "uri",
    "modality",
    "endpoints",
    "input_cost",
    "output_cost",
    "tokens",
    "decision_limits",
    "verified",
    "source",
    "checked_on",
}


def test_the_seed_lists_each_model_once():
    """A uri listed twice would upsert one row with whichever entry came last."""
    uris = [entry["uri"] for entry in _seed()]
    assert len(uris) == len(set(uris))
    assert uris, "the curated seed is empty"


@pytest.mark.parametrize("entry", _seed(), ids=lambda e: e["uri"])
def test_every_seed_entry_carries_the_contract_fields(entry):
    """C7.2's fields are present, nothing unknown is, and every enum value is one budapp knows."""
    assert set(entry) >= REQUIRED_SEED_KEYS, f"missing {sorted(REQUIRED_SEED_KEYS - set(entry))}"
    unknown = set(entry) - REQUIRED_SEED_KEYS - {"cache_cost", "deprecation_date", "note", "details"}
    assert not unknown, f"unknown keys {sorted(unknown)}"
    for value in entry["modality"]:
        M(value)
    for value in entry["endpoints"]:
        E(value)


@pytest.mark.parametrize("entry", _seed(), ids=lambda e: e["uri"])
def test_tc_cat_06_a_seed_model_is_listed_only_under_a_decisions_provider(entry):
    """A seed model under a provider without `decisions` would lose its only route to the gate."""
    provider = entry["uri"].split("/", 1)[0]
    assert provider in _providers(), f"{entry['uri']} names provider {provider!r}, which the catalog lacks"
    assert "/v1/decisions" in entry["endpoints"]
    assert "decisions" in _providers()[provider]["capabilities"]


@pytest.mark.parametrize("entry", _seed(), ids=lambda e: e["uri"])
def test_every_decisions_model_is_priced_per_token_or_per_request(entry):
    """FRD D-25: an unpriced decisions deployment bills nothing; budapp needs a rate to suggest."""
    input_cost = entry["input_cost"] or {}
    per_token = input_cost.get("input_cost_per_token")
    per_request = input_cost.get("input_cost_per_request")
    assert (per_token is not None) != (per_request is not None), "exactly one of per-token or per-request"
    price = per_token if per_token is not None else per_request
    assert isinstance(price, (int, float)) and not isinstance(price, bool) and price > 0
    if per_token is not None:
        output = (entry["output_cost"] or {}).get("output_cost_per_token")
        assert isinstance(output, (int, float)) and output >= 0


@pytest.mark.parametrize("entry", [e for e in _seed() if e["endpoints"] == ["/v1/decisions"]], ids=lambda e: e["uri"])
def test_a_decision_only_model_bills_no_output(entry):
    """Every decision vendor bills input only; output tokens are reported but free (SPIKE.md)."""
    output = (entry["output_cost"] or {}).get("output_cost_per_token", 0)
    assert output == 0


@pytest.mark.parametrize("entry", _seed(), ids=lambda e: e["uri"])
def test_decision_limits_use_the_contract_keys_and_bounds(entry):
    """Limits are C7.2 keys, valid, and never looser than the gateway's own C1.4 bounds."""
    limits = entry["decision_limits"]
    assert isinstance(limits, dict)
    assert set(limits) <= LIMIT_KEYS, f"unknown limit keys {sorted(set(limits) - LIMIT_KEYS)}"
    DecisionLimits(**limits)
    # Tighter than C1.4 or equal, never looser: the gateway applies C1.4 first.
    assert 1 <= limits.get("max_questions", 400) <= 400
    assert 2 <= limits.get("max_choices", 255) <= 255
    assert 2 <= limits.get("max_levels", 10) <= 10


@pytest.mark.parametrize(
    "entry", [e for e in _seed() if not e["uri"].startswith(("openai/", "azure/"))], ids=lambda e: e["uri"]
)
def test_a_system_one_vendor_takes_no_images_in_dm1(entry):
    """C3.3: an `input_image` is a 400 before any System One call in DM1, whatever the vendor accepts."""
    assert entry["decision_limits"].get("images") is False


@pytest.mark.parametrize("entry", _seed(), ids=lambda e: e["uri"])
def test_every_entry_says_where_its_values_came_from(entry):
    """An unverified row is copied from public docs; the URL and the date are how anyone re-checks it."""
    assert isinstance(entry["verified"], bool)
    assert isinstance(entry["source"], str) and entry["source"].startswith("https://")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["checked_on"])


def test_only_the_spiked_models_are_marked_verified():
    """`verified` means a live call passed (SPIKE.md), nothing less."""
    assert {e["uri"] for e in _seed() if e["verified"]} == VERIFIED


def test_the_verified_typesafe_values_are_the_spikes():
    """TypeSafe Jev: $0.042/M input, output free, 64K context, 255 choices, 10 levels, no images."""
    by_uri = _seed_by_uri()
    for uri in ("typesafe/jev-latest", "typesafe/jev-1.14.0", "typesafe/jev-1.13.0"):
        entry = by_uri[uri]
        assert entry["endpoints"] == ["/v1/decisions"]
        assert entry["input_cost"] == {"input_cost_per_token": 4.2e-08}
        assert entry["output_cost"] == {"output_cost_per_token": 0}
        assert entry["tokens"] == {"max_input_tokens": 65536}
        assert entry["decision_limits"] == {"max_choices": 255, "max_levels": 10, "images": False}


def test_the_verified_embedding_studio_values_are_the_spikes():
    """Priced per record, with no token usage at all (FRD D-25, CONTRACTS C7.3)."""
    entry = _seed_by_uri()["embedding_space/laya"]
    assert entry["endpoints"] == ["/v1/decisions"]
    assert entry["input_cost"] == {"input_cost_per_request": 0.002}
    assert entry["decision_limits"] == {"max_questions": 400, "max_choices": 128, "max_levels": 10, "images": False}


@pytest.mark.parametrize("uri", ["openai/gpt-6-luna", "azure/gpt-6-luna"])
def test_luna_serves_chat_responses_and_decisions(uri):
    """Luna is a chat model that also answers decisions (SPIKE.md); the seed keeps every route."""
    entry = _seed_by_uri()[uri]
    assert set(entry["endpoints"]) == {"/v1/chat/completions", "/v1/responses", "/v1/decisions"}
    # $0.10/M input on both routes; output $0.50/M on chat and free on decisions.
    assert entry["input_cost"]["input_cost_per_token"] == 1e-07
    assert entry["input_cost"]["input_cost_per_token_decisions"] == 1e-07
    assert entry["output_cost"]["output_cost_per_token"] == 5e-07
    assert entry["output_cost"]["output_cost_per_token_decisions"] == 0


def test_gpt_5_6_luna_is_not_seeded_as_a_decision_model():
    """OpenAI answers /v1/decisions for gpt-5.6-luna with 404 model_not_found."""
    assert not any("gpt-5.6-luna" in uri for uri in _seed_by_uri())


# ---- C7.2: the merge into a catalog version ------------------------------------------------------ #


def test_a_curated_model_the_sdk_lacks_is_added_under_its_provider(tz, monkeypatch):
    """TypeSafe is not in the SDK's provider map, so Jev comes from the seed alone."""
    infos = _seed_snapshot(tz, monkeypatch, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    jev = infos["typesafe/jev-latest"]
    assert jev.endpoints == [E.DECISIONS]
    assert set(jev.modality) == {M.TEXT_INPUT, M.TEXT_OUTPUT}
    dumped = jev.model_dump()
    assert dumped["input_cost"] == {"input_cost_per_token": 4.2e-08}
    assert dumped["output_cost"] == {"output_cost_per_token": 0}
    assert dumped["tokens"] == {"max_input_tokens": 65536}
    assert dumped["decision_limits"] == {"max_choices": 255, "max_levels": 10, "images": False}


def test_every_curated_model_survives_the_whole_derivation(tz, monkeypatch):
    """The curated seed must not depend on the SDK listing anything but one ordinary model."""
    infos = _seed_snapshot(tz, monkeypatch, {"anthropic/claude-x": {"litellm_provider": "anthropic", "mode": "chat"}})
    for entry in _seed():
        info = infos[entry["uri"]]
        assert sorted(e.value for e in info.endpoints) == sorted(entry["endpoints"]), entry["uri"]
        assert info.model_dump()["decision_limits"] == entry["decision_limits"], entry["uri"]


def test_the_sdks_values_win_and_the_seed_fills_the_rest(tz, monkeypatch):
    """C7.3: use what LiteLLM has; curate only the rest. LiteLLM's openai entry already lists decisions."""
    newer_price = {**LITELLM_GPT_6_LUNA, "input_cost_per_token": 9e-08}
    infos = _seed_snapshot(tz, monkeypatch, {"openai/gpt-6-luna": newer_price})
    luna = infos["openai/gpt-6-luna"].model_dump()
    assert luna["input_cost"]["input_cost_per_token"] == 9e-08
    assert E.BATCH in infos["openai/gpt-6-luna"].endpoints, "the SDK's own routes are kept"
    assert E.DECISIONS in infos["openai/gpt-6-luna"].endpoints
    assert luna["decision_limits"] == _seed_by_uri()["openai/gpt-6-luna"]["decision_limits"]


def test_azure_luna_gains_the_route_litellm_does_not_list(tz, monkeypatch):
    """LiteLLM lists Azure's Luna at chat and responses only."""
    infos = _seed_snapshot(
        tz,
        monkeypatch,
        {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA, "azure/gpt-6-luna": LITELLM_AZURE_GPT_6_LUNA},
    )
    assert infos["azure/gpt-6-luna"].endpoints == [E.CHAT, E.DECISIONS, E.RESPONSE]


def test_a_mode_only_catalog_entry_keeps_its_mode_routes_when_merged(tz, monkeypatch):
    """Merging an explicit list into an entry that had none must not take its mode's routes away."""
    mode_only = {k: v for k, v in LITELLM_AZURE_GPT_6_LUNA.items() if k != "supported_endpoints"}
    mode_only["supported_modalities"] = ["text"]  # a text chat model's mode routes: chat and completions
    infos = _seed_snapshot(tz, monkeypatch, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA, "azure/gpt-6-luna": mode_only})
    assert infos["azure/gpt-6-luna"].endpoints == [E.CHAT, E.COMPLETION, E.DECISIONS, E.RESPONSE]


def test_the_merge_does_not_mask_an_empty_catalog(tz, monkeypatch):
    """The curated seed is a few models; seeding it alone would retire every other model."""
    _fake_sdk(monkeypatch, {})
    with pytest.raises(SeederException):
        asyncio.run(tz.TensorZeroParser.parse_model_data())


def test_the_curated_providers_do_not_trip_the_unknown_provider_guard(tz, monkeypatch):
    """parse_model_data refuses a provider missing from the catalog; the seed's providers are in it."""
    infos = _seed_snapshot(tz, monkeypatch, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    assert "embedding_space/laya" in infos


def test_a_per_request_price_is_priced_not_unknown(tz, monkeypatch):
    """Embedding Studio has no token usage; its price is per record (D-25)."""
    infos = _seed_snapshot(tz, monkeypatch, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    laya = infos["embedding_space/laya"]
    assert laya.model_dump()["input_cost"] == {"input_cost_per_request": 0.002}
    assert laya.billing is not None
    assert laya.billing.confidence is PriceConfidenceEnum.CURATED
    assert laya.billing.unit.value == "request"


def test_a_curated_price_records_its_provenance(tz, monkeypatch):
    """`billing.source` is how a stale hand-copied rate is found again."""
    infos = _seed_snapshot(tz, monkeypatch, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    for uri in ("typesafe/jev-latest", "perplexity/pplx-decider-v1.2"):
        entry = _seed_by_uri()[uri]
        billing = infos[uri].billing
        assert billing.confidence is PriceConfidenceEnum.CURATED
        assert billing.unit.value == "token"
        assert billing.source.url == entry["source"]
        assert billing.source.checked_on


def test_an_unverified_model_says_so_in_its_provenance(tz, monkeypatch):
    """A docs-only price must not read like a live-checked one."""
    infos = _seed_snapshot(tz, monkeypatch, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    assert "not verified" in infos["subq/subq-snap-preview"].billing.source.note
    verified_note = infos["typesafe/jev-latest"].billing.source.note
    assert verified_note.startswith("Verified by a live call") and "not verified" not in verified_note


def test_a_malformed_seed_fails_the_sync_loudly(tz, monkeypatch, tmp_path):
    """A bad hand edit must stop the sync, not publish a model with no price or a wrong route."""
    bad = tmp_path / "decision_models.json"
    bad.write_text(json.dumps([{"uri": "typesafe/jev-latest", "endpoints": ["/v1/decisions"]}]))
    monkeypatch.setattr(tz, "DECISION_MODELS_PATH", str(bad))
    _fake_sdk(monkeypatch, {"openai/gpt-6-luna": dict(LITELLM_GPT_6_LUNA)})
    with pytest.raises(SeederException):
        asyncio.run(tz.TensorZeroParser.parse_model_data())


def test_a_seed_model_under_an_unknown_provider_fails_the_sync(tz, monkeypatch, tmp_path):
    """A provider prefix the catalog lacks would abort the sync later, less clearly."""
    entry = dict(_seed_by_uri()["typesafe/jev-latest"], uri="nobody/jev-latest")
    bad = tmp_path / "decision_models.json"
    bad.write_text(json.dumps([entry]))
    monkeypatch.setattr(tz, "DECISION_MODELS_PATH", str(bad))
    _fake_sdk(monkeypatch, {"openai/gpt-6-luna": dict(LITELLM_GPT_6_LUNA)})
    with pytest.raises(SeederException):
        asyncio.run(tz.TensorZeroParser.parse_model_data())


# ---- C7.2: what the catalog says about each model ------------------------------------------------- #
#
# budadmin's model cards and budCustomer's catalog read `cloud_model.description` (and strengths,
# limitations, use cases, languages, website and GitHub links), which budapp's catalog sync copies
# from the `details` block of /model/get-compatible-models?include_details=true -- that is, from
# bud-connect's `model_details` row for the model. A decision model with no row shows "No
# description available". Most models get their row from `data/model_details.json`, which only the
# startup seeder applies; a curated decision model carries its own `details` block, which the
# catalog sync writes, so the row exists wherever the model does.

MODEL_DETAILS_PATH = REPO_ROOT / "budconnect" / "seeders" / "data" / "model_details.json"

#: The `model_details` columns a curated `details` block fills, in that table's own names.
CURATED_DETAIL_COLUMNS = ("description", "advantages", "disadvantages", "use_cases", "languages")


_MODEL_DETAILS_CACHE: dict = {}


def _model_details():
    """data/model_details.json, by uri; read once (it is several megabytes)."""
    if not _MODEL_DETAILS_CACHE:
        with MODEL_DETAILS_PATH.open() as handle:
            _MODEL_DETAILS_CACHE.update(json.load(handle))
    return _MODEL_DETAILS_CACHE


class _RecordingCRUD:
    """A ProviderCRUD / ModelInfoCRUD / ModelDetailsCRUD double recording each upsert and its id."""

    def __init__(self, sink):
        self.sink = sink

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def upsert(self, data, conflict_target=None, **kwargs):
        row_id = uuid.uuid4()
        self.sink.append({"data": dict(data), "conflict_target": conflict_target, "id": row_id})
        return row_id

    def add_engine_version(self, row_id, version_id):
        return None


class _EngineCRUD:
    def __init__(self, engine):
        self.engine = engine

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def get_session(self):
        import contextlib
        from unittest.mock import MagicMock

        return contextlib.nullcontext(MagicMock())

    def fetch_one(self, conditions, session):
        return self.engine


def _run_seed(tz, monkeypatch, tmp_path, sdk_models):
    """Run TensorZeroSeeder.seed over a fake, trusted SDK catalog; return what it upserted, by table."""
    from unittest.mock import MagicMock

    written = {"provider": [], "model_info": [], "model_details": []}
    engine = types.SimpleNamespace(versions=[types.SimpleNamespace(version="0.1.0", id=uuid.uuid4())])
    data_file = tmp_path / "models.json"
    data_file.write_text("{}")

    async def no_licenses(self):
        return {}

    async def version_file(version):
        return str(data_file)

    _fake_sdk(monkeypatch, {uri: dict(config) for uri, config in sdk_models.items()})
    monkeypatch.setattr(tz, "EngineCRUD", lambda: _EngineCRUD(engine))
    monkeypatch.setattr(tz, "ProviderCRUD", lambda: _RecordingCRUD(written["provider"]))
    monkeypatch.setattr(tz, "ModelInfoCRUD", lambda: _RecordingCRUD(written["model_info"]))
    monkeypatch.setattr(tz, "ModelDetailsCRUD", lambda: _RecordingCRUD(written["model_details"]), raising=False)
    monkeypatch.setattr(tz.TensorZeroSeeder, "get_license_id_map", no_licenses)
    monkeypatch.setattr(tz.TensorZeroSeeder, "get_version_file_path", staticmethod(version_file))
    monkeypatch.setattr(tz.TensorZeroSeeder, "get_existing_provider_types", lambda self, vid: {})
    monkeypatch.setattr(tz.TensorZeroSeeder, "get_existing_model_uris", lambda self, vid: {})
    monkeypatch.setattr(tz.TensorZeroSeeder, "deactivate_stale_providers", MagicMock(return_value=0))
    monkeypatch.setattr(tz.TensorZeroSeeder, "deactivate_stale_models", MagicMock(return_value=0))
    asyncio.run(tz.TensorZeroSeeder().seed())
    return written


@pytest.mark.parametrize("entry", _seed(), ids=lambda e: e["uri"])
def test_every_decision_model_has_a_description(entry):
    """Without one, every decision model card reads "No description available"."""
    details = entry.get("details") or _model_details().get(entry["uri"]) or {}
    description = details.get("description")
    assert isinstance(description, str) and description.strip(), f"{entry['uri']} has no description"


@pytest.mark.parametrize("entry", [e for e in _seed() if "details" in e], ids=lambda e: e["uri"])
def test_a_curated_details_block_never_shadows_model_details_json(entry):
    """Two writers of one row -- the startup seeder and the sync -- would swap its text on every run."""
    assert entry["uri"] not in _model_details(), f"{entry['uri']} is described in both files; keep one"


@pytest.mark.parametrize("entry", [e for e in _seed() if "details" in e], ids=lambda e: e["uri"])
def test_a_curated_details_block_says_where_it_came_from(entry):
    """Every block cites the vendor pages it was read from, so a stale claim can be re-checked."""
    details = entry["details"]
    assert details["sources"], f"{entry['uri']} cites no source"
    for source in details["sources"]:
        assert source["url"].startswith("https://")
        assert source["kind"] in {"maker", "host", "third_party"}
        assert source["title"].strip()
    for field in ("website_url", "github_url"):
        assert details.get(field) is None or details[field].startswith("https://"), field
    for field in CURATED_DETAIL_COLUMNS[1:]:
        values = details.get(field, [])
        assert isinstance(values, list) and all(isinstance(v, str) and v.strip() for v in values), field


def test_the_curated_details_reach_the_row_the_seeder_upserts(tz, monkeypatch, tmp_path):
    """Each curated block is upserted into `model_details`, keyed on the model_info row it describes."""
    written = _run_seed(tz, monkeypatch, tmp_path, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    info_ids = {row["data"]["uri"]: row["id"] for row in written["model_info"]}
    details_by_id = {}
    for row in written["model_details"]:
        assert row["conflict_target"] == ["model_info_id"]
        details_by_id.setdefault(row["data"]["model_info_id"], []).append(row["data"])

    described = [e for e in _seed() if "details" in e]
    assert described, "no curated entry carries details"
    for entry in described:
        rows = details_by_id.get(info_ids[entry["uri"]], [])
        assert len(rows) == 1, f"{entry['uri']}: {len(rows)} details upserts"
        row, details = rows[0], entry["details"]
        for column in CURATED_DETAIL_COLUMNS:
            assert row[column] == details.get(column, []), (entry["uri"], column)
        assert row["website_url"] == details.get("website_url")
        assert row["github_url"] == details.get("github_url")
        metadata = row["extraction_metadata"]
        assert metadata["sources"] == details["sources"]
        assert metadata["extraction_date"] == entry["checked_on"]
        assert metadata["method"] == "curated"
    assert len(written["model_details"]) == len(described), "only curated blocks are written"


def test_a_model_described_by_model_details_json_gets_no_curated_row(tz, monkeypatch, tmp_path):
    """gpt-6-luna's research lives in model_details.json; the sync must not overwrite it."""
    written = _run_seed(tz, monkeypatch, tmp_path, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    luna = {row["id"] for row in written["model_info"] if row["data"]["uri"] == "openai/gpt-6-luna"}
    assert luna
    assert not [row for row in written["model_details"] if row["data"]["model_info_id"] in luna]


def test_the_details_block_never_reaches_the_model_info_row(tz, monkeypatch, tmp_path):
    """`model_info` has no such columns; the block must not leak into its upsert."""
    written = _run_seed(tz, monkeypatch, tmp_path, {"openai/gpt-6-luna": LITELLM_GPT_6_LUNA})
    for row in written["model_info"]:
        assert "details" not in row["data"]
        assert "description" not in row["data"]


@pytest.mark.parametrize(
    "details",
    [
        {"description": "", "sources": [{"kind": "maker", "title": "Docs", "url": "https://example.com"}]},
        {"description": "A model.", "sources": []},
        {"description": "A model.", "sources": [{"kind": "maker", "title": "Docs", "url": "http://example.com"}]},
        {
            "description": "A model.",
            "website_url": "example.com",
            "sources": [{"kind": "maker", "title": "Docs", "url": "https://example.com"}],
        },
        {
            "description": "A model.",
            "strengths": ["fast"],
            "sources": [{"kind": "maker", "title": "Docs", "url": "https://example.com"}],
        },
        {
            "description": "A model.",
            "use_cases": [""],
            "sources": [{"kind": "maker", "title": "Docs", "url": "https://example.com"}],
        },
        "A model.",
    ],
    ids=["empty-description", "no-source", "http-source", "bare-website", "unknown-key", "blank-item", "not-object"],
)
def test_a_malformed_details_block_fails_the_sync(tz, monkeypatch, tmp_path, details):
    """Caught at load, in CI, rather than written into the row budapp copies to every catalog."""
    entry = dict(_seed_by_uri()["typesafe/jev-latest"], details=details)
    bad = tmp_path / "decision_models.json"
    bad.write_text(json.dumps([entry]))
    monkeypatch.setattr(tz, "DECISION_MODELS_PATH", str(bad))
    with pytest.raises(SeederException, match=r"jev-latest: details (is invalid|must be an object)"):
        tz.load_decision_models()
