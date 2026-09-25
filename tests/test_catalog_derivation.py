"""How a catalog entry becomes routes, prices and a sync decision.

Every case here is one that shipped wrong and was found by comparing the live catalog against
what each model actually is: Sora published as a chat model, an embedding model with no
embeddings route, thirteen realtime models advertising speech routes they cannot serve, OCR
and gpt-image prices dropped on the floor, and a sync that would have retired the whole
catalog on an empty upstream file.

The seeder module is loaded with its package stubbed out: ``budconnect/seeders/__init__.py``
imports every seeder, which pulls in auth dependencies and a circular import that the rest of
this suite sidesteps by parsing source with ``ast``. These tests need the real functions.
"""

import asyncio
import importlib
import sys
import types
import uuid

import pytest

from budconnect.commons.constants import ModelEndpointEnum as E
from budconnect.commons.constants import ProviderCapabilityEnum as C
from budconnect.commons.exceptions import SeederException
from budconnect.model.schemas import InputCost, LiteLLMModelInfo, OutputCost


@pytest.fixture(scope="module")
def tz():
    """Load the real seeder module without its package's import side effects."""
    saved = {k: sys.modules.get(k) for k in ("budconnect.seeders", "budconnect.seeders.tensorzero")}
    import budconnect

    pkg = types.ModuleType("budconnect.seeders")
    pkg.__path__ = [str(__import__("pathlib").Path(budconnect.__file__).parent / "seeders")]
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


def routes(tz, uri, **config):
    """Return the routes derive_model_specs gives a catalog entry with this config."""
    specs = asyncio.run(tz.TensorZeroParser.derive_model_specs(LiteLLMModelInfo(uri=uri, config=config)))
    return set(specs["endpoints"])


# --------------------------------------------------------------------------------- #
# routes come from the mode, not from capability flags
# --------------------------------------------------------------------------------- #


def test_a_video_model_is_not_a_chat_model(tz):
    """azure/sora-2 was published at /v1/chat/completions from its text-input flag."""
    assert routes(tz, "azure/sora-2", mode="video_generation", supported_modalities=["text"]) == set()


def test_a_realtime_model_gets_no_route_whatever_its_flags(tz):
    """A realtime model gets no route, whatever its flags.

    Thirteen had speech and transcription routes, which kept them out of the "no route" set
    budapp hides.
    """
    assert (
        routes(
            tz,
            "azure/us/gpt-4o-realtime-preview-2024-12-17",
            mode="realtime",
            supported_modalities=["text", "audio"],
            supported_output_modalities=["text", "audio"],
            supports_audio_input=True,
            supports_audio_output=True,
        )
        == set()
    )


def test_an_embedding_model_is_served_at_embeddings(tz):
    """gemini-embedding-2 had chat + transcription routes and no /v1/embeddings at all."""
    assert routes(
        tz, "gemini/gemini-embedding-2", mode="embedding", supports_audio_input=True, supports_vision=True
    ) == {E.EMBEDDING}


def test_image_input_does_not_make_a_model_an_image_generator(tz):
    """Titan's image embedder and Llama 4's vision models were offered image generation."""
    assert routes(tz, "bedrock/amazon.titan-embed-image-v1", mode="embedding", supports_image_input=True) == {
        E.EMBEDDING
    }
    assert E.IMAGE_GENERATION not in routes(tz, "bedrock/meta.llama4-scout", mode="chat", supports_image_input=True)


def test_an_audio_capable_chat_model_keeps_its_chat_route(tz):
    """voxtral-small (audio input) and gpt-4o-audio-preview lost CHAT entirely."""
    assert routes(tz, "mistral/voxtral-small-latest", mode="chat", supports_audio_input=True) == {E.CHAT}
    assert routes(
        tz, "openai/gpt-4o-audio-preview", mode="chat", supports_audio_input=True, supports_audio_output=True
    ) == {E.CHAT}


def test_a_text_chat_model_keeps_completions(tz):
    """The chat models that had /v1/completions before keep it."""
    assert routes(tz, "gemini/x", mode="chat", supported_modalities=["text"]) == {E.CHAT, E.COMPLETION}


def test_batch_alone_is_not_a_route(tz):
    """BATCH alone is a way of calling a route, not a route.

    Mistral OCR is listed at /v1/ocr and /v1/batch; with /v1/ocr unservable, BATCH alone made
    it look deployable.
    """
    assert routes(tz, "mistral/mistral-ocr-latest", mode="ocr", supported_endpoints=["/v1/ocr", "/v1/batch"]) == set()


def test_an_explicit_endpoint_list_is_still_authoritative(tz):
    """Where LiteLLM says a model is served, that wins over its mode."""
    assert routes(
        tz,
        "gemini/gemini-3.1-flash-image",
        mode="image_generation",
        supported_endpoints=["/v1/chat/completions", "/v1/batch"],
    ) == {E.CHAT, E.BATCH}


# --------------------------------------------------------------------------------- #
# audio routes a voice vendor's gateway cannot dispatch
# --------------------------------------------------------------------------------- #


def test_a_voice_vendor_without_tts_loses_its_speech_route(tz):
    """Groq is a WaaV STT vendor with no WaaV TTS; its Orpheus voices failed every request."""
    groq = [C.MODEL, C.AUDIO_TRANSCRIPTION, C.AUDIO_TRANSLATION]
    assert tz.gate_audio_routes([E.AUDIO_SPEECH], groq) == []
    assert tz.gate_audio_routes([E.AUDIO_TRANSCRIPTION], groq) == [E.AUDIO_TRANSCRIPTION]


def test_a_provider_with_no_audio_capability_is_left_alone(tz):
    """Its audio models go to budgateway, not WaaV; this gate says nothing about those."""
    assert tz.gate_audio_routes([E.AUDIO_SPEECH, E.CHAT], [C.MODEL]) == [E.AUDIO_SPEECH, E.CHAT]


def test_a_full_voice_vendor_keeps_every_route(tz):
    """OpenAI claims both TTS and STT, so neither route is dropped."""
    openai = [C.MODEL, C.AUDIO_TRANSCRIPTION, C.AUDIO_TRANSLATION, C.TEXT_TO_SPEECH]
    assert tz.gate_audio_routes([E.AUDIO_SPEECH, E.AUDIO_TRANSCRIPTION], openai) == [
        E.AUDIO_SPEECH,
        E.AUDIO_TRANSCRIPTION,
    ]


# --------------------------------------------------------------------------------- #
# prices the schema did not name
# --------------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("field", "bucket"),
    [
        ("output_cost_per_image_token", "output_cost"),
        ("input_cost_per_token_above_272k_tokens", "input_cost"),
        ("output_cost_per_token_priority", "output_cost"),
        ("cache_creation_input_token_cost_above_1hr", "cache_cost"),
        ("ocr_cost_per_page", "input_cost"),
        ("annotation_cost_per_page_batches", "input_cost"),
        ("output_cost_per_video_per_second", "output_cost"),
    ],
)
def test_an_unlisted_price_is_kept_in_its_bucket(tz, field, bucket):
    """Each of these was dropped by the old whitelist."""
    assert tz.price_category(field, 1e-06) == bucket


@pytest.mark.parametrize(
    ("field", "value"), [("max_tokens", 4096), ("supports_vision", True), ("input_cost_per_token", "x")]
)
def test_things_that_are_not_prices_are_not_bucketed(tz, field, value):
    """Limits, flags and non-numbers stay out of the cost columns."""
    assert tz.price_category(field, value) is None


def test_gpt_image_output_is_no_longer_free(tz):
    """output_cost_per_image_token ($8/M) was dropped, leaving gpt-image output unpriced."""
    mi = asyncio.run(
        tz.TensorZeroParser().create_model_info(
            LiteLLMModelInfo(
                uri="azure/gpt-image-1-mini",
                config={
                    "mode": "image_generation",
                    "input_cost_per_token": 2e-06,
                    "output_cost_per_image_token": 8e-06,
                },
            ),
            uuid.uuid4(),
            "azure",
            None,
        )
    )
    assert mi.model_dump()["output_cost"] == {"output_cost_per_image_token": 8e-06}


def test_a_model_priced_per_page_is_not_marked_unpriced(tz):
    """Mistral OCR was stamped confidence=unknown ("no price found") beside a published price."""
    mi = asyncio.run(
        tz.TensorZeroParser().create_model_info(
            LiteLLMModelInfo(uri="mistral/mistral-ocr-4", config={"mode": "ocr", "ocr_cost_per_page": 0.004}),
            uuid.uuid4(),
            "mistral",
            None,
        )
    )
    assert mi.billing is None
    assert mi.model_dump()["input_cost"] == {"ocr_cost_per_page": 0.004}


def test_the_cost_schemas_still_refuse_what_is_not_a_price():
    """Allowing unnamed price fields must not let arbitrary keys through."""
    with pytest.raises(ValueError):
        InputCost(max_tokens=4096)
    with pytest.raises(ValueError):
        OutputCost(output_cost_per_image_token="free")
    with pytest.raises(ValueError):
        InputCost(output_cost_per_token=1e-06)  # right shape, wrong bucket
    assert InputCost(input_cost_per_token_priority=5e-06).model_dump()["input_cost_per_token_priority"] == 5e-06


# --------------------------------------------------------------------------------- #
# a catalog the seeder must not act on
# --------------------------------------------------------------------------------- #


def _fake_sdk(monkeypatch, models, ai_models_fetched_at="2026-09-24"):
    class Result:
        def __init__(self):
            self.models = models
            self.ai_models_fetched_at = ai_models_fetched_at
            self.stats = types.SimpleNamespace(matched=0, unmatched=0)

    class CatalogClient:
        def fetch_catalog_sync(self):
            return Result()

    monkeypatch.setitem(sys.modules, "bud_model_catalog", types.SimpleNamespace(CatalogClient=CatalogClient))


def test_an_empty_catalog_is_refused(tz, monkeypatch):
    """Seeding one retired every model and unlinked every provider (reproduced with a stub)."""
    _fake_sdk(monkeypatch, {})
    with pytest.raises(SeederException, match="no models"):
        asyncio.run(tz.TensorZeroParser.parse_model_data())


def test_a_degraded_catalog_is_refused(tz, monkeypatch):
    """With ai-models down, 240 deprecated models came back and 87 prices changed."""
    _fake_sdk(monkeypatch, {"openai/gpt-4o": {"litellm_provider": "openai", "mode": "chat"}}, None)
    with pytest.raises(SeederException, match="ai-models"):
        asyncio.run(tz.TensorZeroParser.parse_model_data())


def test_ordinary_churn_is_retired(tz):
    """A handful of models leaving the catalog is normal and goes through."""
    tz.refuse_mass_retirement("0.1.0", {f"m{i}" for i in range(10)}, 1535)


def test_retiring_a_fifth_of_the_catalog_at_once_is_refused(tz):
    """A truncated catalog passes the empty guard and would retire what it lost."""
    with pytest.raises(SeederException, match="looks truncated"):
        tz.refuse_mass_retirement("0.1.0", {f"m{i}" for i in range(400)}, 1535)


def test_a_small_catalog_can_still_lose_a_few(tz):
    """The fraction has a floor, or a six-model catalog could never retire one."""
    tz.refuse_mass_retirement("0.1.0", {f"m{i}" for i in range(6)}, 6)
