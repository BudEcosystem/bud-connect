"""Which catalog models are served at ``/v1/realtime`` (FRD-023 RT1.6, CONTRACTS.md C5).

``/v1/realtime`` is the OpenAI Realtime GA socket that WaaV relays for Bud deployments. budapp
publishes a deployment carrying it to the audio plane, so the route is a promise that WaaV can
open that socket for that model. Two ways to break the promise, both tested here:

* the wrong MODEL gets the route (TC-CAT-04). LiteLLM files every live-audio model under
  ``mode: "realtime"`` whatever protocol it speaks -- GPT-Live (``gpt-live-1``, NG-1), the
  translation sessions (``gpt-realtime-translate``, NG-2), the retired ``gpt-4o-*-realtime-preview``
  betas, Gemini Live, Nova Sonic. What says a model speaks the Realtime protocol is an explicit
  ``/v1/realtime`` in its ``supported_endpoints``. And a chat model that also lists
  ``/v1/realtime`` (``gpt-audio-mini``) stays a chat model: a deployment is published to one
  plane, and the chat plane is the one its chat route needs.
* the wrong PROVIDER keeps it (TC-CAT-05). WaaV relays OpenAI and Azure only until RT7 (DEG-1),
  so a model under a provider without ``realtime_session`` loses the route, loudly.

The entries below are copied from the catalog SDK's output (2026-09-28, the fields that decide
routes and prices), not written from memory: the first draft of this rule assumed
``gpt-live-1`` carried no realtime mode, and it does.

Loads the seeder module with its package stubbed out, like ``test_catalog_derivation``.
"""

import asyncio
import importlib
import logging
import re
import sys
import types
import uuid
from pathlib import Path

import pytest

from budconnect.commons.constants import ModelEndpointEnum as E
from budconnect.commons.constants import ProviderCapabilityEnum as C
from budconnect.model.schemas import LiteLLMModelInfo


REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = REPO_ROOT / "alembic" / "versions"


# ---- catalog entries, as the SDK emits them -------------------------------------------------- #

GPT_REALTIME_2_1 = {
    "litellm_provider": "openai",
    "mode": "realtime",
    "supported_endpoints": ["/v1/realtime"],
    "supported_modalities": ["text", "image", "audio"],
    "supported_output_modalities": ["text", "audio"],
    "supports_audio_input": True,
    "supports_audio_output": True,
    "input_cost_per_token": 4e-06,
    "input_cost_per_audio_token": 3.2e-05,
    "input_cost_per_image_token": 5e-06,
    "output_cost_per_token": 2.4e-05,
    "output_cost_per_audio_token": 6.4e-05,
    "cache_read_input_token_cost": 4e-07,
    "cache_read_input_audio_token_cost": 4e-07,
}

#: GPT-Live: audio in and out, `mode: "realtime"`, and a different protocol (NG-1).
GPT_LIVE_1 = {
    "litellm_provider": "openai",
    "mode": "realtime",
    "supported_modalities": ["text", "audio"],
    "supported_output_modalities": ["text", "audio"],
    "supports_audio_input": True,
    "supports_audio_output": True,
}

GPT_AUDIO_1_5 = {
    "litellm_provider": "openai",
    "mode": "chat",
    "supported_endpoints": ["/v1/chat/completions"],
    "supported_modalities": ["text", "audio"],
    "supported_output_modalities": ["text", "audio"],
    "supports_audio_input": True,
    "supports_audio_output": True,
    "supports_vision": False,
}

#: A chat model that LiteLLM ALSO lists at /v1/realtime.
GPT_AUDIO_MINI = {
    "litellm_provider": "openai",
    "mode": "chat",
    "supported_endpoints": ["/v1/chat/completions", "/v1/responses", "/v1/realtime", "/v1/batch"],
    "supported_modalities": ["text", "audio"],
    "supported_output_modalities": ["text", "audio"],
    "supports_audio_input": True,
    "supports_audio_output": True,
    "supports_vision": False,
}

#: A transcription session model: served at /v1/realtime with no audio output, which is what
#: budapp derives `session_type: "transcription"` from.
GPT_REALTIME_WHISPER = {
    "litellm_provider": "openai",
    "mode": "audio_transcription",
    "supported_endpoints": ["/v1/realtime", "/v1/realtime/transcription_sessions"],
    "supported_modalities": ["audio"],
    "supported_output_modalities": ["text"],
    "supports_audio_input": True,
}

#: The translation sessions (NG-2): `mode: "realtime"`, a separate protocol, no endpoint list.
GPT_REALTIME_TRANSLATE = {
    "litellm_provider": "openai",
    "mode": "realtime",
    "supported_modalities": ["audio"],
    "supported_output_modalities": ["text", "audio"],
    "supports_audio_input": True,
    "supports_audio_output": True,
}

#: A retired beta-protocol model: `mode: "realtime"`, no endpoint list, no modalities.
GPT_4O_MINI_REALTIME_PREVIEW = {
    "litellm_provider": "openai",
    "mode": "realtime",
    "supports_audio_input": True,
    "supports_audio_output": True,
}


#: Gemini Live is listed at /v1/realtime, and WaaV has no Gemini translator until RT7.
GEMINI_3_8_LIVE = {
    "litellm_provider": "gemini",
    "mode": "realtime",
    "supported_endpoints": ["/v1/realtime"],
    "supported_modalities": ["text", "image", "audio", "video"],
    "supported_output_modalities": ["text", "audio"],
    "supports_audio_input": True,
    "supports_audio_output": True,
    "supports_vision": True,
}


# ---- helpers --------------------------------------------------------------------------------- #


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


# ---- C5 vocabulary --------------------------------------------------------------------------- #


def test_the_realtime_route_and_capability_carry_the_contract_values():
    """Budapp matches these strings exactly; its sync drops or refuses anything else."""
    assert E.REALTIME.value == "/v1/realtime"
    assert C.REALTIME_SESSION.value == "realtime_session"


def test_the_capability_filter_cannot_confuse_realtime_session_with_another_capability():
    """`get_providers_by_capability` matches a NAME as a substring of the joined array.

    So a capability whose name contains another's would be returned for both.
    """
    names = [c.name for c in C]
    for name in names:
        for other in names:
            if name != other:
                assert other not in name, f"filtering on {other} would also match providers declaring {name}"


def _migration_labels(enum_name):
    """Labels every migration adds to a PG enum through `ALTER TYPE ... ADD VALUE`, by file."""
    pattern = re.compile(rf"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '([A-Z_]+)'")
    found = {}
    for path in MIGRATIONS_DIR.glob("*.py"):
        for label in pattern.findall(path.read_text()):
            found.setdefault(label, []).append(path.name)
    return found


@pytest.mark.parametrize(
    ("column", "member", "pg_type"),
    [("endpoints", E.REALTIME, "modelendpointenum"), ("capabilities", C.REALTIME_SESSION, "providercapabilityenum")],
)
def test_one_migration_adds_the_label_the_orm_writes(column, member, pg_type):
    """The columns store member NAMES (no `values_callable`), so the PG label is the name.

    Without it the first seed carrying the value fails its INSERT with "invalid input value
    for enum".
    """
    from budconnect.model.models import ModelInfo, Provider

    table = ModelInfo if column == "endpoints" else Provider
    orm_labels = table.__table__.c[column].type.item_type.enums
    assert member.name in orm_labels, f"the ORM would not write {member.name}"
    assert len(_migration_labels(pg_type).get(member.name, [])) == 1, (
        f"exactly one migration must add {member.name!r} to {pg_type}"
    )


# ---- TC-CAT-04: realtime is per model, never inferred from modality or mode ------------------- #


@pytest.mark.parametrize(
    ("uri", "config"),
    [("openai/gpt-realtime-2.1", GPT_REALTIME_2_1), ("openai/gpt-realtime-whisper", GPT_REALTIME_WHISPER)],
)
def test_an_explicit_realtime_listing_derives_the_route(tz, uri, config):
    """Before FRD-023 the value did not exist and the route was dropped with a warning."""
    assert _routes(tz, uri, config) == [E.REALTIME]


@pytest.mark.parametrize(
    ("uri", "config"),
    [
        ("openai/gpt-live-1", GPT_LIVE_1),
        ("openai/gpt-realtime-translate", GPT_REALTIME_TRANSLATE),
        ("openai/gpt-4o-mini-realtime-preview-2024-12-17", GPT_4O_MINI_REALTIME_PREVIEW),
    ],
)
def test_realtime_mode_alone_is_not_the_realtime_protocol(tz, uri, config):
    """LiteLLM's `realtime` mode covers GPT-Live, translation and the retired betas.

    None of them speaks the Realtime GA protocol, and none carries an explicit /v1/realtime.
    """
    assert _routes(tz, uri, config) == []


def test_a_chat_model_listed_at_realtime_stays_a_chat_model(tz):
    """gpt-audio-mini keeps chat, responses and batch; /v1/realtime would move it off the chat plane."""
    assert _routes(tz, "openai/gpt-audio-mini-2025-12-15", GPT_AUDIO_MINI) == [E.BATCH, E.CHAT, E.RESPONSE]


def test_audio_in_and_out_never_implies_realtime(tz):
    """A model with every audio flag and no endpoint list gets its mode's route, not realtime."""
    config = {"mode": "chat", "supports_audio_input": True, "supports_audio_output": True}
    assert _routes(tz, "openai/gpt-4o-audio-preview", config) == [E.CHAT]


# ---- TC-CAT-05: a provider without realtime_session loses the route --------------------------- #


def test_tc_cat_05_a_provider_without_the_capability_loses_the_route_with_a_warning(tz, caplog):
    """Gemini lists its Live models at /v1/realtime; WaaV cannot serve them until RT7 (TC-CAT-05)."""
    with caplog.at_level(logging.WARNING, logger=tz.logger.name):
        mi = _model_info(tz, "gemini/gemini-3.8-live", GEMINI_3_8_LIVE, "gemini")

    assert mi.endpoints == []
    warnings = [
        r for r in caplog.records if r.levelno == logging.WARNING and "gemini/gemini-3.8-live" in r.getMessage()
    ]
    assert any("realtime_session" in r.getMessage() for r in warnings), [r.getMessage() for r in caplog.records]


def test_the_gate_removes_only_the_realtime_route(tz):
    """Chirp is listed at transcriptions AND realtime; only the route WaaV cannot serve goes."""
    assert tz.gate_realtime_route([E.AUDIO_TRANSCRIPTION, E.REALTIME], [C.MODEL], "vertex/chirp_3") == [
        E.AUDIO_TRANSCRIPTION
    ]


def test_the_gate_keeps_the_route_for_a_provider_that_declares_it(tz, caplog):
    """OpenAI and Azure keep it, silently."""
    with caplog.at_level(logging.WARNING, logger=tz.logger.name):
        assert tz.gate_realtime_route([E.REALTIME], [C.MODEL, C.REALTIME_SESSION], "openai/gpt-realtime") == [
            E.REALTIME
        ]
    assert not caplog.records


def test_the_gate_is_silent_for_a_model_with_no_realtime_route(tz, caplog):
    """Warning on every chat model of every provider would bury the one that matters."""
    with caplog.at_level(logging.WARNING, logger=tz.logger.name):
        assert tz.gate_realtime_route([E.CHAT], [C.MODEL], "gemini/gemini-3-pro") == [E.CHAT]
    assert not caplog.records


def test_the_gate_applies_through_the_provider_catalog(tz, monkeypatch):
    """create_model_info reads the provider's capabilities from the catalog JSON, not the entry."""
    monkeypatch.setattr(tz, "_PROVIDER_CAPABILITIES", {"openai": ["model"]})
    assert _model_info(tz, "openai/gpt-realtime-2.1", GPT_REALTIME_2_1, "openai").endpoints == []
