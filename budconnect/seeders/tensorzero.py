#  -----------------------------------------------------------------------------
#  Copyright (c) 2024 Bud Ecosystem Inc.
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  -----------------------------------------------------------------------------

"""The TensorZero seeder, containing essential data structures for the TensorZero microservice."""

import json
import os
import re
from datetime import date
from typing import Any, Dict, FrozenSet, List, Optional, Set
from uuid import UUID

from budmicroframe.commons import logging
from sqlalchemy import delete

from budconnect.seeders.constants import NO_MODEL_PROVIDERS

from ..commons.constants import (
    BillingUnitEnum,
    ModalityEnum,
    ModelEndpointEnum,
    ModelStatusEnum,
    PriceConfidenceEnum,
    ProviderCapabilityEnum,
)
from ..commons.exceptions import SeederException
from ..engine.crud import EngineCRUD
from ..model.crud import LicenseCRUD, ModelDetailsCRUD, ModelInfoCRUD, ProviderCRUD
from ..model.models import ModelInfo, Provider, engine_version_model_info, engine_version_provider
from ..model.schemas import (
    Billing,
    CacheCost,
    CuratedModelDetails,
    DecisionLimits,
    Features,
    InputCost,
    LiteLLMModelInfo,
    MediaLimits,
    ModelInfoCreate,
    OutputCost,
    ProviderCreate,
    RateLimits,
    SearchContextCost,
    Tokens,
)
from .base import BaseSeeder


logger = logging.get_logger(__name__)


# Pre-defined paths
SEEDER_DIR = os.path.dirname(os.path.abspath(__file__))
TENSORZERO_DATA_DIR = os.path.join(SEEDER_DIR, "data", "tensorzero")
TENSORZERO_PROVIDERS_PATH = os.path.join(TENSORZERO_DATA_DIR, "tensorzero_providers.json")
#: Decision models the catalog SDK does not carry, merged into every version (bud-runtime spec 031 C7.2).
DECISION_MODELS_PATH = os.path.join(SEEDER_DIR, "data", "decisions", "decision_models.json")
LICENSES_PATH = os.path.join(SEEDER_DIR, "data", "licenses.json")

#: The most of a version's models one sync may retire, as a fraction and as a floor (so a
#: small catalog can still lose a few). See the guard in `TensorZeroSeeder.seed`.
MAX_RETIREMENT_FRACTION = 0.2
MIN_RETIREMENT_ALLOWANCE = 25

#: The route a model is served at, by LiteLLM `mode`, for a model that lists no
#: `supported_endpoints` of its own. A mode missing here -- realtime, video_generation, ocr --
#: has no Bud route, so its models get none, which is what budapp hides them by.
#:
#: `realtime` is missing on purpose, although /v1/realtime is a Bud route (FRD-023). LiteLLM
#: files every live-audio model under `mode: "realtime"` whatever protocol it speaks: GPT-Live
#: (`gpt-live-1`, a different socket), the translation sessions (`gpt-realtime-translate`), the
#: retired `gpt-4o-*-realtime-preview` betas, Gemini Live, Nova Sonic. Among OpenAI and Azure
#: models, the mode-only set is exactly those -- every GA `gpt-realtime*` model lists
#: /v1/realtime explicitly. So the mode would add only routes that fail at connect time; the
#: explicit list is what says a model speaks the Realtime protocol.
#:
#: `decisions` and `evaluation` are missing for the same reason (bud-runtime spec 031 C7.3). LiteLLM
#: files decision models under both -- `decisions` for four (Baseten, a Fireworks Rune path) and
#: `evaluation` for thirty-five (TypeSafe Jev, Perplexity Decider, Cloudflare Clef, ...) as of
#: 2026-11-08 -- and `evaluation` does not even say decisions. A model is served at /v1/decisions when
#: its entry lists that route (or /v1/systemone, its other name) explicitly, as gpt-6-luna does, or
#: when the curated seed (`DECISION_MODELS_PATH`) says so.
MODE_ENDPOINTS: Dict[str, List[ModelEndpointEnum]] = {
    "chat": [ModelEndpointEnum.CHAT],
    "completion": [ModelEndpointEnum.COMPLETION],
    "responses": [ModelEndpointEnum.RESPONSE],
    "embedding": [ModelEndpointEnum.EMBEDDING],
    "image_generation": [ModelEndpointEnum.IMAGE_GENERATION],
    # An image in, an image out, with an optional prompt: the shape of /v1/images/edits.
    "image_edit": [ModelEndpointEnum.IMAGE_EDIT],
    "audio_transcription": [ModelEndpointEnum.AUDIO_TRANSCRIPTION],
    "audio_speech": [ModelEndpointEnum.AUDIO_SPEECH],
    "moderation": [ModelEndpointEnum.MODERATION],
    "rerank": [ModelEndpointEnum.RERANK],
}

#: Modalities by mode, for a model whose entry declares none.
MODE_MODALITIES: Dict[str, List[ModalityEnum]] = {
    "chat": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
    "completion": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
    "responses": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
    "embedding": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
    "image_generation": [ModalityEnum.TEXT_INPUT, ModalityEnum.IMAGE_OUTPUT],
    "image_edit": [ModalityEnum.TEXT_INPUT, ModalityEnum.IMAGE_INPUT, ModalityEnum.IMAGE_OUTPUT],
    "audio_transcription": [ModalityEnum.AUDIO_INPUT, ModalityEnum.TEXT_OUTPUT],
    "audio_speech": [ModalityEnum.TEXT_INPUT, ModalityEnum.AUDIO_OUTPUT],
    "moderation": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
    "rerank": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
    "ocr": [ModalityEnum.IMAGE_INPUT, ModalityEnum.TEXT_OUTPUT],
}

#: Audio route -> the provider capability that says the audio gateway can serve it.
AUDIO_ROUTE_CAPABILITY: Dict[ModelEndpointEnum, ProviderCapabilityEnum] = {
    ModelEndpointEnum.AUDIO_SPEECH: ProviderCapabilityEnum.TEXT_TO_SPEECH,
    ModelEndpointEnum.AUDIO_TRANSCRIPTION: ProviderCapabilityEnum.AUDIO_TRANSCRIPTION,
    ModelEndpointEnum.AUDIO_TRANSLATION: ProviderCapabilityEnum.AUDIO_TRANSLATION,
}


def gate_audio_routes(
    endpoints: List[ModelEndpointEnum], capabilities: List[ProviderCapabilityEnum]
) -> List[ModelEndpointEnum]:
    """Drop audio routes a voice provider's own capabilities say the gateway cannot serve.

    A provider that declares ANY audio capability is a voice vendor: budapp publishes its
    audio-only deployments to WaaV, and the capabilities are checked against what WaaV can
    dispatch (tests/test_voice_providers.py). So for such a provider a TTS model under a
    vendor with no TEXT_TO_SPEECH is a model WaaV will refuse -- Groq's Orpheus voices,
    which LiteLLM lists and WaaV has no Groq TTS for, failed every request with "Unknown
    TTS provider". Left with no route, the model is hidden like any other unservable one.

    A provider with no audio capability is untouched: its audio models are served by
    budgateway, not WaaV, and this says nothing about what budgateway can do.
    """
    if not any(cap in AUDIO_ROUTE_CAPABILITY.values() for cap in capabilities):
        return endpoints
    return [e for e in endpoints if e not in AUDIO_ROUTE_CAPABILITY or AUDIO_ROUTE_CAPABILITY[e] in capabilities]


#: The modes whose models keep an explicit /v1/realtime: speech-to-speech models and realtime
#: transcription models (`gpt-realtime-whisper`, the `session_type: "transcription"` deployments).
#: A chat model LiteLLM also lists there -- `gpt-audio-mini` lists chat, responses, realtime and
#: batch -- stays a chat model: budapp publishes a deployment to ONE plane, and a realtime route
#: would take it off the chat plane its chat route needs (FRD-023 §5.12, CONTRACTS C5).
REALTIME_MODES = frozenset({"realtime", "audio_transcription"})


def gate_realtime_route(
    endpoints: List[ModelEndpointEnum], capabilities: List[ProviderCapabilityEnum], uri: str
) -> List[ModelEndpointEnum]:
    """Drop /v1/realtime from a model whose provider the audio gateway cannot open a session for.

    Unlike `gate_audio_routes` this applies to EVERY provider: /v1/realtime is only ever served
    by WaaV, so a provider without `realtime_session` has no other plane to fall back to. WaaV
    serves OpenAI, Azure OpenAI and xAI by relay and Gemini Live, Nova 2 Sonic and the per-minute
    agents by translation (FRD-023 C7); Vertex, which LiteLLM also lists Live models for, has no
    translator (DEG-1). Loud, because it is the one place a model the source calls
    realtime-capable silently loses the route.
    """
    if ModelEndpointEnum.REALTIME not in endpoints or ProviderCapabilityEnum.REALTIME_SESSION in capabilities:
        return endpoints
    logger.warning(
        "Model %s is listed at %s, but its provider does not declare %s; the route is dropped",
        uri,
        ModelEndpointEnum.REALTIME.value,
        ProviderCapabilityEnum.REALTIME_SESSION.value,
    )
    return [e for e in endpoints if e is not ModelEndpointEnum.REALTIME]


def gate_decisions_route(
    endpoints: List[ModelEndpointEnum], capabilities: List[ProviderCapabilityEnum], uri: str
) -> List[ModelEndpointEnum]:
    """Drop /v1/decisions from a model whose provider budgateway cannot serve that route for.

    bud-runtime spec 031 C7.3. budapp publishes a deployment carrying /v1/decisions either natively
    (OpenAI, Azure) or as a System One entry whose URL is the provider's ``decisions_url`` -- a field
    only providers declaring ``decisions`` carry. Under any other provider the route has no URL to
    call and every request would fail, so it goes. Loud, like `gate_realtime_route`: it is the one
    place a model the source lists at the route silently loses it. Each model is derived once per
    version, so this logs once per model per sync.
    """
    if ModelEndpointEnum.DECISIONS not in endpoints or ProviderCapabilityEnum.DECISIONS in capabilities:
        return endpoints
    logger.warning(
        "Model %s is listed at %s, but its provider does not declare %s; the route is dropped",
        uri,
        ModelEndpointEnum.DECISIONS.value,
        ProviderCapabilityEnum.DECISIONS.value,
    )
    return [e for e in endpoints if e is not ModelEndpointEnum.DECISIONS]


#: Routes a source lists under another name, by that name. `/v1/systemone` is the System One shape of
#: the decisions capability; Bud serves both routes for any deployment carrying /v1/decisions.
ENDPOINT_ALIASES: Dict[str, ModelEndpointEnum] = {"/v1/systemone": ModelEndpointEnum.DECISIONS}


def mode_routes(config: Dict[str, Any]) -> List[ModelEndpointEnum]:
    """Return the routes a catalog entry gets from its LiteLLM `mode`, for when it lists none of its own."""
    mode = config.get("mode") or ""
    routes = list(MODE_ENDPOINTS.get(mode, ()))
    if mode == "chat" and "text" in config.get("supported_modalities", []):
        # Kept from the flag-derived routes this replaced, so the models that had
        # /v1/completions beside chat keep it; it is the same text-generation family.
        routes.append(ModelEndpointEnum.COMPLETION)
    return routes


#: FRD-023 RT7, CONTRACTS C5/C7. Realtime models LiteLLM lists with NO endpoint list, granted
#: /v1/realtime by NAME -- per model, never from their mode (which would also grant GPT-Live, the
#: translation sessions and the retired betas). By provider_type, the bare model id.
#:
#: Nova 2 Sonic is the one such model WaaV serves (its translate engine over Bedrock's
#: InvokeModelWithBidirectionalStream). What is NOT here, deliberately: xAI's voice model
#: (``grok-voice-*``) is not in the catalog at all, and the per-minute agents (Deepgram Voice Agent,
#: ElevenLabs Agents, Hume EVI) are agents, not models -- their own flow, a later phase. None is
#: invented here, and their providers do not declare ``realtime_session``: a declaration puts a
#: provider in budadmin's Realtime picker, which would then show an empty list.
REALTIME_ROUTE_GRANTS: Dict[str, FrozenSet[str]] = {
    "bedrock": frozenset({"amazon.nova-2-sonic-v1:0"}),
}

#: Providers WaaV serves as speech-to-speech sessions ONLY (C7): its translate engine (Gemini Live,
#: Nova 2 Sonic), xAI, and the per-minute agents. A realtime TRANSCRIPTION model under one of them
#: (``gemini-3.5-transcribe-live``) would publish a session type none of them opens, so it keeps no
#: /v1/realtime. OpenAI and Azure serve both session types (``gpt-realtime-whisper``).
SPEECH_TO_SPEECH_ONLY_REALTIME_PROVIDERS = frozenset({"gemini", "bedrock", "xai", "deepgram", "elevenlabs", "hume"})

#: A speech TRANSLATION session model (FRD-023 NG-2): ``gpt-realtime-translate``,
#: ``gemini-3.5-live-translate-preview``. Its own product and protocol, whatever it is listed at.
_TRANSLATION_SESSION_RE = re.compile(r"(?:live|realtime)-translate")


def realtime_route_for_model(
    endpoints: List[ModelEndpointEnum], provider_type: str, uri: str, mode: str
) -> List[ModelEndpointEnum]:
    """Grant or withhold /v1/realtime for one model (FRD-023 C5, C7), before the provider gates.

    Grants it to a model named in :data:`REALTIME_ROUTE_GRANTS`; withholds it from a translation
    session (NG-2), and from a non-``realtime``-mode model under a speech-to-speech-only provider.
    Whether the provider can serve the route at all is still :func:`gate_realtime_route`'s question.
    """
    bare = uri.split("/", 1)[1] if uri.startswith(f"{provider_type}/") else uri
    routes = set(endpoints)
    if bare in REALTIME_ROUTE_GRANTS.get(provider_type, frozenset()):
        routes.add(ModelEndpointEnum.REALTIME)
    if ModelEndpointEnum.REALTIME in routes:
        reason = None
        if _TRANSLATION_SESSION_RE.search(uri):
            reason = "it is a speech translation session, not a conversation (FRD-023 NG-2)"
        elif provider_type in SPEECH_TO_SPEECH_ONLY_REALTIME_PROVIDERS and mode != "realtime":
            reason = f"{provider_type} realtime sessions are speech-to-speech only and its mode is {mode!r}"
        if reason:
            # Not a warning: the rule working, on every sync, for the same few models.
            logger.info(
                "Model %s is listed at %s; the route is withheld: %s", uri, ModelEndpointEnum.REALTIME.value, reason
            )
            routes.discard(ModelEndpointEnum.REALTIME)
    return sorted(routes, key=lambda e: e.value)


def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read and parse JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the parsed JSON data

    Raises:
        FileNotFoundError: If the file is not found
    """
    if not os.path.exists(file_path):
        logger.error("file not found at %s", file_path)
        raise FileNotFoundError(f"file not found at {file_path}")

    with open(file_path, "r") as f:
        data: Dict[str, Any] = json.load(f)
        return data


def is_fine_tune_price_key(uri: str) -> bool:
    """Whether a catalog key is LiteLLM's price entry for fine-tunes rather than a model.

    LiteLLM lists `ft:gpt-4o-mini-2024-07-18` so it can price calls to any fine-tune of that
    base. A fine-tuned model's id carries the owner after the base,
    `ft:gpt-4o-mini-2024-07-18:<org>:<suffix>:<id>`, so the bare prefix is no model at all:
    OpenAI answers `model_not_found` to every request. Published as a chat model, it could be
    deployed, and every request to the deployment failed with a 502.
    """
    return uri.split("/", 1)[-1].startswith("ft:")


def refuse_mass_retirement(version: str, stale_uris: Set[str], existing_count: int) -> None:
    """Raise rather than retire an implausible share of a version's models in one run.

    A catalog that is present but truncated -- a reshaped upstream file, a provider mapping
    lost in an SDK change -- passes the empty-catalog guard and would retire whatever it
    lost. Real churn is a handful of models a night; a fifth of the catalog at once is a
    broken input. Raised after the upserts, so what the run did fetch is still written.
    """
    limit = max(MIN_RETIREMENT_ALLOWANCE, int(existing_count * MAX_RETIREMENT_FRACTION))
    if len(stale_uris) > limit:
        raise SeederException(
            f"Refusing to retire {len(stale_uris)} of {existing_count} models for version {version} "
            f"in one run (limit {limit}); the catalog looks truncated. Sample: {sorted(stale_uris)[:10]}"
        )


def price_category(field: str, value: Any) -> Optional[str]:
    """Which cost bucket an unlisted LiteLLM price field belongs in, or None if it is not one.

    CONFIG_FIELD_MAPPING names the fields that existed when it was written; LiteLLM keeps
    adding more (`*_above_272k_tokens`, `*_priority`, `*_flex`, `output_cost_per_image_token`,
    `ocr_cost_per_page`). Anything unlisted used to be dropped silently, so this sorts a
    price by its prefix instead. Charges levied per page, query or session are input-side:
    they are paid for what is sent, like a per-request price.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)) or "cost" not in field:
        return None
    if field.startswith("output_"):
        return "output_cost"
    if field.startswith("cache_"):
        return "cache_cost"
    if field.startswith(("input_", "ocr_", "annotation_", "google_maps_", "code_interpreter_")):
        return "input_cost"
    return None


_PROVIDER_CAPABILITIES: Optional[Dict[str, List[str]]] = None


def _provider_capabilities() -> Dict[str, List[str]]:
    """provider_type -> capability values, from the provider catalog; read once per process."""
    global _PROVIDER_CAPABILITIES
    if _PROVIDER_CAPABILITIES is None:
        _PROVIDER_CAPABILITIES = {
            ptype: entry.get("capabilities", []) for ptype, entry in read_json_file(TENSORZERO_PROVIDERS_PATH).items()
        }
    return _PROVIDER_CAPABILITIES


#: The fields a curated decision model must carry (bud-runtime spec 031 C7.2), and the ones it may.
CURATED_REQUIRED_KEYS: FrozenSet[str] = frozenset(
    {
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
)
CURATED_OPTIONAL_KEYS: FrozenSet[str] = frozenset({"cache_cost", "deprecation_date", "note", "details"})

#: The blocks of a curated entry that are LiteLLM fields grouped by kind; flattened back for the parser.
_CURATED_FLAT_BLOCKS = ("input_cost", "output_cost", "cache_cost", "tokens")


def _is_price(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _curated_entry_problems(entry: Any, providers: Dict[str, Any]) -> List[str]:
    """Everything wrong with one curated decision model; empty when it can be seeded."""
    if not isinstance(entry, dict):
        return [f"entry {entry!r} is not an object"]
    uri = entry.get("uri")
    missing = sorted(CURATED_REQUIRED_KEYS - set(entry))
    if missing:
        return [f"{uri}: missing {missing}"]
    problems = []
    unknown = sorted(set(entry) - CURATED_REQUIRED_KEYS - CURATED_OPTIONAL_KEYS)
    if unknown:
        problems.append(f"{uri}: unknown keys {unknown}")

    provider = uri.split("/", 1)[0] if isinstance(uri, str) and "/" in uri else None
    if provider not in providers:
        problems.append(f"{uri}: the provider prefix is not a provider in {TENSORZERO_PROVIDERS_PATH}")
    elif ProviderCapabilityEnum.DECISIONS.value not in providers[provider].get("capabilities", []):
        problems.append(f"{uri}: provider {provider} does not declare {ProviderCapabilityEnum.DECISIONS.value}")

    try:
        if not entry["modality"]:
            problems.append(f"{uri}: no modality")
        for value in entry["modality"]:
            ModalityEnum(value)
        routes = [ModelEndpointEnum(value) for value in entry["endpoints"]]
        if ModelEndpointEnum.DECISIONS not in routes:
            problems.append(f"{uri}: not listed at {ModelEndpointEnum.DECISIONS.value}")
    except (TypeError, ValueError) as e:
        problems.append(f"{uri}: {e}")

    # Priced per token or per request (FRD D-25), never both and never neither: an unpriced
    # decisions deployment would bill nothing.
    input_cost = entry["input_cost"] if isinstance(entry["input_cost"], dict) else {}
    per_token, per_request = input_cost.get("input_cost_per_token"), input_cost.get("input_cost_per_request")
    if (per_token is None) == (per_request is None) or not _is_price(
        per_token if per_token is not None else per_request
    ):
        problems.append(f"{uri}: needs exactly one positive input_cost_per_token or input_cost_per_request")

    for block, schema in (
        ("input_cost", InputCost),
        ("output_cost", OutputCost),
        ("cache_cost", CacheCost),
        ("tokens", Tokens),
        ("decision_limits", DecisionLimits),
    ):
        value = entry.get(block)
        if value is None and block != "decision_limits":
            continue
        if not isinstance(value, dict):
            problems.append(f"{uri}: {block} must be an object")
            continue
        try:
            schema(**value)
        except (TypeError, ValueError) as e:
            problems.append(f"{uri}: {block} is invalid: {e}")

    if "details" in entry:
        if not isinstance(entry["details"], dict):
            problems.append(f"{uri}: details must be an object")
        else:
            try:
                CuratedModelDetails(**entry["details"])
            except (TypeError, ValueError) as e:
                problems.append(f"{uri}: details is invalid: {e}")

    if not isinstance(entry["verified"], bool):
        problems.append(f"{uri}: verified must be true or false")
    if not (isinstance(entry["source"], str) and entry["source"].startswith("https://")):
        problems.append(f"{uri}: source must be an https URL")
    try:
        date.fromisoformat(entry["checked_on"])
    except (TypeError, ValueError):
        problems.append(f"{uri}: checked_on must be an ISO date")
    return problems


def load_decision_models() -> List[Dict[str, Any]]:
    """Read and validate the curated decision models (bud-runtime spec 031 C7.2).

    A problem in the file fails the sync -- which keeps yesterday's rows -- rather than seeding a
    decision model with no price, under a provider that cannot serve it, or with limits nobody can
    enforce. The file ships with the image, so CI is where such a problem is meant to be caught.

    Raises:
        SeederException: The file is missing, unreadable, or holds an entry that cannot be seeded.
    """
    try:
        with open(DECISION_MODELS_PATH, "r") as f:
            entries: Any = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise SeederException(f"Cannot read the curated decision models at {DECISION_MODELS_PATH}: {e}") from e
    if not isinstance(entries, list):
        raise SeederException(f"{DECISION_MODELS_PATH} must hold a list of models")

    providers = read_json_file(TENSORZERO_PROVIDERS_PATH)
    problems = [problem for entry in entries for problem in _curated_entry_problems(entry, providers)]
    uris = [entry["uri"] for entry in entries if isinstance(entry, dict) and "uri" in entry]
    duplicates = sorted({uri for uri in uris if uris.count(uri) > 1})
    if duplicates:
        problems.append(f"listed more than once: {duplicates}")
    if problems:
        raise SeederException(f"Refusing to seed the curated decision models: {'; '.join(problems)}")
    return entries


def curated_details_row(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return the ``model_details`` columns a curated entry fills, or None when it has no ``details``.

    budapp's catalog sync reads a model's description, strengths, limitations, use cases, languages
    and links from its ``model_details`` row (``/model/get-compatible-models?include_details``). Most
    rows come from ``data/model_details.json``, which only the startup seeder applies; a curated
    decision model's row is written by the catalog sync itself, so it exists wherever the model does.
    Every column the block owns is written, empty lists included, so a claim removed from the file is
    removed from the row. The pages it was read from go to ``extraction_metadata``, as in that file.
    """
    if entry.get("details") is None:
        return None
    details = CuratedModelDetails(**entry["details"])
    return {
        "description": details.description,
        "advantages": details.advantages,
        "disadvantages": details.disadvantages,
        "use_cases": details.use_cases,
        "languages": details.languages,
        "website_url": details.website_url,
        "github_url": details.github_url,
        "extraction_metadata": {
            "method": "curated",
            "extraction_date": entry["checked_on"],
            "provider": entry["uri"].split("/", 1)[0],
            "sources": [source.model_dump() for source in details.sources],
        },
    }


def curated_model_config(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Put a curated decision model in the catalog SDK's shape, so it takes the same derivation path.

    Modalities go back to LiteLLM's `supported_modalities` words and the cost and token blocks are
    flattened to their LiteLLM field names, which `create_model_info` sorts into the same blocks
    again. The endpoint list is explicit, so the route never depends on a mode (C7.3). The price's
    provenance becomes a `billing` block, the field bud-connect already carries it in.
    """
    config: Dict[str, Any] = {
        "litellm_provider": entry["uri"].split("/", 1)[0],
        "supported_endpoints": list(entry["endpoints"]),
    }
    inputs = [m.rsplit("_", 1)[0] for m in entry["modality"] if m.endswith("_input")]
    outputs = [m.rsplit("_", 1)[0] for m in entry["modality"] if m.endswith("_output")]
    if inputs:
        config["supported_modalities"] = inputs
    if outputs:
        config["supported_output_modalities"] = outputs
    for block in _CURATED_FLAT_BLOCKS:
        config.update(entry.get(block) or {})
    if entry.get("deprecation_date"):
        config["deprecation_date"] = entry["deprecation_date"]
    config["decision_limits"] = dict(entry["decision_limits"])
    details = curated_details_row(entry)
    if details is not None:
        config["details"] = details

    if entry["verified"]:
        note = f"Verified by a live call on {entry['checked_on']} (bud-runtime spec 031, SPIKE.md)."
    else:
        note = "Copied from public documentation; not verified by a live call."
    if entry.get("note"):
        note = f"{note} {entry['note']}"
    per_request = "input_cost_per_request" in (entry["input_cost"] or {})
    config["billing"] = {
        "unit": BillingUnitEnum.REQUEST.value if per_request else BillingUnitEnum.TOKEN.value,
        "currency": "USD",
        "confidence": PriceConfidenceEnum.CURATED.value,
        "source": {"url": entry["source"], "checked_on": entry["checked_on"], "note": note},
    }
    return config


def _extend_catalog_entry(existing: Dict[str, Any], curated: Dict[str, Any]) -> Dict[str, Any]:
    """Add a curated decision model's routes and missing fields to the SDK's entry for the same model.

    The SDK's values win wherever it has one (C7.3: use what LiteLLM has, curate only the rest). Its
    routes are kept -- the mode's, when it lists none -- and the curated ones are added. A curated
    `billing` block describes the curated price, so it is not attached to a price the SDK supplied.
    """
    entry = dict(existing)
    routes = list(entry.get("supported_endpoints") or [route.value for route in mode_routes(entry)])
    routes.extend(route for route in curated["supported_endpoints"] if route not in routes)
    entry["supported_endpoints"] = routes
    priced_by_sdk = any(price_category(field, value) for field, value in existing.items())
    for field, value in curated.items():
        if field in ("supported_endpoints", "litellm_provider") or (field == "billing" and priced_by_sdk):
            continue
        entry.setdefault(field, value)
    return entry


def merge_decision_models(
    model_data: Dict[str, Dict[str, Any]], curated: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Merge the curated decision models into one catalog fetch (bud-runtime spec 031 C7.2).

    The catalog SDK maps a fixed set of LiteLLM providers, and none of the System One vendors is in
    it, so their models come from here alone. A model the SDK does carry (gpt-6-luna) is extended,
    not replaced. Returns a new mapping; the SDK's entries are not modified.
    """
    merged = dict(model_data)
    added: List[str] = []
    extended: List[str] = []
    for entry in curated:
        uri = entry["uri"]
        config = curated_model_config(entry)
        if uri in merged:
            merged[uri] = _extend_catalog_entry(merged[uri], config)
            extended.append(uri)
        else:
            merged[uri] = config
            added.append(uri)
    logger.info(
        "Merged %d curated decision models: %d added, %d extended (%s)",
        len(curated),
        len(added),
        len(extended),
        ", ".join(extended) or "none",
    )
    return merged


def get_license_key_for_model(model_uri: str, provider_type: str) -> Optional[str]:
    """Get license key for a model based on its URI and provider.

    Args:
        model_uri: The model URI
        provider_type: The provider type

    Returns:
        License key if found, None otherwise
    """
    # This function is now mainly a fallback - most license_id should come directly from model data
    # Return None if we don't have specific knowledge about the license
    return None


class UntrustedCatalogError(SeederException):
    """The catalog SDK's fetch is empty or degraded, so the sync must not act on it.

    A subclass, so every existing handler of ``SeederException`` still sees a failed sync. It is
    told apart only so that ``TensorZeroSeeder.seed`` can still apply the curated decision models
    -- our own validated file -- additively before failing (bud-runtime spec 031 C7.2).
    """


class TensorZeroParser:
    """Parser for TensorZero model data.

    This class contains methods to parse and transform TensorZero model data
    from the source format to a structure suitable for database insertion.
    """

    @staticmethod
    async def parse_model_data() -> Dict[str, List[LiteLLMModelInfo]]:
        """Fetch TensorZero model data from the catalog SDK and organize by provider.

        Returns:
            Dict mapping providers to their models with model details

        Raises:
            SeederException: If there is an error parsing the model data
        """
        # TODO: (Remove it after testing) Old file-based loading (replaced by catalog SDK):
        # model_data = read_json_file(str(source_path))
        # logger.debug("Loaded %d models from TensorZero data file", len(model_data))

        # Fetch model data from the catalog SDK
        from bud_model_catalog import CatalogClient

        result = CatalogClient().fetch_catalog_sync()
        model_data = result.models

        # Both guards turn a bad catalog into a failed sync, which keeps yesterday's rows,
        # instead of a "successful" one that rewrites them. The seeder reads absence from a
        # run as retirement, so what it must never do is act on a catalog it cannot trust.
        if not model_data:
            # The SDK returns an empty catalog, rather than raising, when LiteLLM answers
            # with nothing usable -- and says so, expecting the consumer to notice. Seeding
            # it would retire every model and unlink every provider.
            raise UntrustedCatalogError("Catalog SDK returned no models; refusing to sync an empty catalog")
        if result.ai_models_fetched_at is None:
            # ai-models failed and the SDK fell back to LiteLLM alone. That catalog filters
            # deprecations by LiteLLM's dates only and prices from LiteLLM only: measured,
            # 240 deprecated models come back and 87 prices change, for one night, until the
            # next good run retires them again -- and budapp mirrors each flip.
            raise UntrustedCatalogError(
                "ai-models source was unavailable, so the catalog is LiteLLM-only (deprecated "
                "models resurface, prices regress); keeping the previous catalog"
            )
        logger.info(
            "Fetched %d models from catalog SDK (matched=%d, unmatched=%d)",
            len(model_data),
            result.stats.matched,
            result.stats.unmatched,
        )

        price_keys = sorted(uri for uri in model_data if is_fine_tune_price_key(uri))
        if price_keys:
            # Dropped after the guards, so they judge the catalog as fetched. Seeded earlier,
            # these entries are now absent and retire like any model that left the catalog.
            logger.info("Dropping %d fine-tune price keys, which are not models: %s", len(price_keys), price_keys)
            model_data = {uri: info for uri, info in model_data.items() if not is_fine_tune_price_key(uri)}

        # Merged after the guards, so they judge the SDK's catalog alone: a few curated decision
        # models must never make an empty or degraded catalog look seedable.
        model_data = merge_decision_models(model_data, load_decision_models())
        return TensorZeroParser.group_by_provider(model_data)

    @staticmethod
    async def parse_curated_decision_models() -> Dict[str, List[LiteLLMModelInfo]]:
        """Return the curated decision models alone, organised by provider (C7.2).

        What ``TensorZeroSeeder.seed`` applies while the SDK's fetch is untrusted. Without the SDK
        there is nothing to extend, so each curated entry is complete on its own -- gpt-6-luna
        carries its chat price in the file for exactly this case.
        """
        return TensorZeroParser.group_by_provider(merge_decision_models({}, load_decision_models()))

    @staticmethod
    def group_by_provider(model_data: Dict[str, Dict[str, Any]]) -> Dict[str, List[LiteLLMModelInfo]]:
        """Organise one catalog fetch by provider, refusing a provider with no catalog entry.

        Raises:
            SeederException: A model names a provider ``tensorzero_providers.json`` does not define.
        """
        # Get unique providers
        providers = {item["litellm_provider"] for item in model_data.values()}
        logger.debug("Found %d providers in TensorZero data", len(providers))

        # Organize models by provider
        provider_model_map = {}
        for provider in providers:
            provider_models = {}
            for model_name, model_info in model_data.items():
                if model_info["litellm_provider"] == provider:
                    provider_models[model_name] = model_info

            provider_model_map[provider] = provider_models

        # Read providers data
        predefined_providers = read_json_file(TENSORZERO_PROVIDERS_PATH)

        # Validate any missing providers with predefined providers
        missing_providers = set(provider_model_map.keys()) - set(predefined_providers.keys())
        if missing_providers:
            logger.warning("Missing providers: %s", missing_providers)
            raise SeederException("New providers found in TensorZero data")

        # Parse models to a common schema
        parsed_model_data: Dict[str, List[LiteLLMModelInfo]] = {}
        for provider, models in provider_model_map.items():
            for model_uri, model_details in models.items():
                if provider not in parsed_model_data:
                    parsed_model_data[provider] = []

                model_details.pop("litellm_provider", None)

                parsed_model_data[provider].append(LiteLLMModelInfo(uri=model_uri, config=model_details))

        return parsed_model_data

    async def create_model_info(
        self, model_data: LiteLLMModelInfo, provider_id: UUID, provider_type: str, license_id: Optional[UUID]
    ) -> ModelInfoCreate:
        """Create a model info from the model data.

        Args:
            model_data: The model data
        """
        # Define explicit mappings for each configuration field to its category
        CONFIG_FIELD_MAPPING = {
            "input_cost_per_audio_per_second": "input_cost",
            "input_cost_per_video_per_second_above_8s_interval": "input_cost",
            "input_cost_per_image": "input_cost",
            "input_cost_per_token_batch_requests": "input_cost",
            "input_cost_per_audio_per_second_above_128k_tokens": "input_cost",
            "input_cost_per_token_cache_hit": "input_cost",
            "input_cost_per_video_per_second_above_15s_interval": "input_cost",
            "input_cost_per_video_per_second": "input_cost",
            "input_cost_per_token_batches": "input_cost",
            "input_cost_per_pixel": "input_cost",
            "input_cost_per_token_above_200k_tokens": "input_cost",
            "input_cost_per_video_per_second_above_128k_tokens": "input_cost",
            "input_cost_per_character": "input_cost",
            "input_cost_per_image_above_128k_tokens": "input_cost",
            "input_cost_per_token_above_128k_tokens": "input_cost",
            "input_cost_per_query": "input_cost",
            "input_cost_per_audio_token": "input_cost",
            "input_cost_per_token": "input_cost",
            "input_cost_per_request": "input_cost",
            "input_cost_per_second": "input_cost",
            "input_cost_per_character_above_128k_tokens": "input_cost",
            "input_dbu_cost_per_token": "input_cost",
            # Output costs
            "output_cost_per_pixel": "output_cost",
            "output_cost_per_token": "output_cost",
            "output_cost_per_character": "output_cost",
            "output_dbu_cost_per_token": "output_cost",
            "output_cost_per_image": "output_cost",
            "output_cost_per_token_above_200k_tokens": "output_cost",
            "output_cost_per_character_above_128k_tokens": "output_cost",
            "output_cost_per_second": "output_cost",
            "output_cost_per_audio_token": "output_cost",
            "output_cost_per_token_batches": "output_cost",
            "output_cost_per_token_above_128k_tokens": "output_cost",
            "output_cost_per_reasoning_token": "output_cost",
            "output_db_cost_per_token": "output_cost",
            # Cache costs
            "cache_read_input_token_cost": "cache_cost",
            "cache_read_input_audio_token_cost": "cache_cost",
            "cache_creation_input_audio_token_cost": "cache_cost",
            "cache_creation_input_token_cost": "cache_cost",
            # Token limits
            "max_input_tokens": "tokens",
            "max_tokens_per_document_chunk": "tokens",
            "max_query_tokens": "tokens",
            "max_output_tokens": "tokens",
            "max_tokens": "tokens",
            "tool_use_system_prompt_tokens": "tokens",
            # Rate limits
            "rpm": "rate_limits",
            "tpm": "rate_limits",
            "rpd": "rate_limits",
            # Media limits
            "max_audio_per_prompt": "media_limits",
            "max_document_chunks_per_query": "media_limits",
            "max_audio_length_hours": "media_limits",
            "max_images_per_prompt": "media_limits",
            "max_videos_per_prompt": "media_limits",
            "max_pdf_size_mb": "media_limits",
            "max_video_length": "media_limits",
            # Features
            "supports_web_search": "features",
            "supports_response_schema": "features",
            "supports_reasoning": "features",
            "supports_system_messages": "features",
            "supports_tool_choice": "features",
            "supports_parallel_function_calling": "features",
            "supports_assistant_prefill": "features",
            "supports_function_calling": "features",
            "supports_native_streaming": "features",
            "supports_prompt_caching": "features",
            # Search context costs
            "search_context_cost_per_query": "search_context_cost",
        }

        # Initialize category dictionaries
        categorized_data: Dict[str, Dict[str, Any]] = {
            "input_cost": {},
            "output_cost": {},
            "cache_cost": {},
            "search_context_cost": {},
            "tokens": {},
            "rate_limits": {},
            "media_limits": {},
            "features": {},
        }

        # Categorize the model data
        for field, value in model_data.config.items():
            category = CONFIG_FIELD_MAPPING.get(field) or price_category(field, value)
            if category:
                categorized_data[category][field] = value

        # Determine the modality of the model
        if model_data.uri in [
            "fireworks-ai-4.1b-to-16b",
            "fireworks-ai-above-16b",
            "fireworks-ai-moe-up-to-56b",
            "fireworks-ai-56b-to-176b",
            "fireworks-ai-default",
            "fireworks-ai-up-to-4b",
            "fireworks-ai-embedding-up-to-150m",
            "fireworks-ai-embedding-150m-to-350m",
        ]:
            model_specs = await self.derive_predefined_model_specs(model_data)
        else:
            model_specs = await self.derive_model_specs(model_data)

        # FRD-023 RT7: per-model realtime grants and withholdings, before the provider gates judge them.
        model_specs["endpoints"] = realtime_route_for_model(
            model_specs["endpoints"], provider_type, model_data.uri, model_data.config.get("mode") or ""
        )
        capabilities = [ProviderCapabilityEnum(c) for c in _provider_capabilities().get(provider_type, [])]
        model_specs["endpoints"] = gate_audio_routes(model_specs["endpoints"], capabilities)
        model_specs["endpoints"] = gate_realtime_route(model_specs["endpoints"], capabilities, model_data.uri)
        model_specs["endpoints"] = gate_decisions_route(model_specs["endpoints"], capabilities, model_data.uri)

        billing = await self.derive_billing(model_data, categorized_data)
        decision_limits = self.derive_decision_limits(model_data, model_specs["endpoints"])

        if categorized_data["search_context_cost"]:
            search_context_cost_per_query = SearchContextCost(
                **categorized_data["search_context_cost"]["search_context_cost_per_query"]
            )
        else:
            search_context_cost_per_query = None

        # Create a model info schema
        return ModelInfoCreate(
            uri=model_data.uri,
            modality=model_specs["modalities"],
            endpoints=model_specs["endpoints"],
            provider_id=provider_id,
            input_cost=InputCost(**categorized_data["input_cost"]) if categorized_data["input_cost"] else None,
            output_cost=OutputCost(**categorized_data["output_cost"]) if categorized_data["output_cost"] else None,
            cache_cost=CacheCost(**categorized_data["cache_cost"]) if categorized_data["cache_cost"] else None,
            search_context_cost_per_query=search_context_cost_per_query,
            tokens=Tokens(**categorized_data["tokens"]) if categorized_data["tokens"] else None,
            rate_limits=RateLimits(**categorized_data["rate_limits"]) if categorized_data["rate_limits"] else None,
            media_limits=MediaLimits(**categorized_data["media_limits"]) if categorized_data["media_limits"] else None,
            features=Features(**categorized_data["features"]) if categorized_data["features"] else None,
            billing=billing,
            decision_limits=decision_limits,
            deprecation_date=model_data.config.get("deprecation_date"),
            license_id=license_id,
            status=ModelStatusEnum.ACTIVE,
        )

    @staticmethod
    def derive_decision_limits(
        model_data: LiteLLMModelInfo, endpoints: List[ModelEndpointEnum]
    ) -> Optional[DecisionLimits]:
        """Return the vendor's per-request caps, for a model that kept its /v1/decisions route.

        The curated seed is validated when it is loaded, so a malformed block can only come from
        the catalog SDK. Like a malformed billing block it costs that model its limits, not every
        provider its sync: with no limits the gateway applies its own and surfaces the vendor's 400.
        """
        declared = model_data.config.get("decision_limits")
        if not declared or ModelEndpointEnum.DECISIONS not in endpoints:
            return None
        try:
            return DecisionLimits(**declared)
        except (TypeError, ValueError):
            logger.warning("Discarding malformed decision_limits for %s: %r", model_data.uri, declared)
            return None

    @staticmethod
    async def derive_billing(model_data: LiteLLMModelInfo, categorized_data: Dict[str, Any]) -> Optional[Billing]:
        """Attach the rules a rate must be applied under, and say when there is no rate.

        Two jobs, and the second is the important one.

        Pass-through: a source that knows the vendor's billing rules -- volume tiers, a
        minimum billable duration, which region the rate was read for -- emits them as a
        ``billing`` block, which is validated and carried. The seeder does not invent these;
        it has no way to know them.

        The UNKNOWN marker: a model arriving with no cost fields at all gets an explicit
        ``confidence=UNKNOWN`` rather than silence. ``input_cost`` is nullable, so "nobody
        could find a price" and "this is free" are otherwise the same absent value, and a
        consumer reading that absence as zero bills nothing and reports nothing. For audio
        this is the common case, not an edge one: Cartesia sells credits and the regional
        vendors quote on contract, so roughly 25 of the voice vendors have no obtainable
        per-unit price.

        Args:
            model_data: The model, whose config may carry a `billing` block from the source.
            categorized_data: Cost fields already sorted into input/output/cache buckets.

        Returns:
            A validated Billing, or None when the model is priced and the source said nothing
            further about how the rate must be applied.
        """
        declared = model_data.config.get("billing")
        if declared:
            try:
                return Billing(**declared)
            except (TypeError, ValueError):
                # One malformed block must not cost every provider its nightly price
                # refresh. Downgrade to "we do not know", which is true, and say so loudly
                # enough that someone fixes the source.
                logger.warning("Discarding malformed billing block for %s: %r", model_data.uri, declared)
                return Billing(confidence=PriceConfidenceEnum.UNKNOWN)

        priced = bool(categorized_data["input_cost"] or categorized_data["output_cost"])
        if not priced:
            return Billing(confidence=PriceConfidenceEnum.UNKNOWN)

        return None

    @staticmethod
    async def derive_predefined_model_specs(model_data: LiteLLMModelInfo) -> Dict[str, Any]:
        """Determine the modality adn endpoints of the predefined model.

        Args:
            model_data: The model data

        Returns:
            The modality and endpoints of the model
        """
        uri = model_data.uri

        if uri in [
            "fireworks-ai-4.1b-to-16b",
            "fireworks-ai-above-16b",
            "fireworks-ai-moe-up-to-56b",
            "fireworks-ai-56b-to-176b",
            "fireworks-ai-default",
            "fireworks-ai-up-to-4b",
        ]:
            return {
                "modalities": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
                "endpoints": [ModelEndpointEnum.COMPLETION, ModelEndpointEnum.CHAT],
            }
        elif uri in [
            "fireworks-ai-embedding-up-to-150m",
            "fireworks-ai-embedding-150m-to-350m",
        ]:
            return {
                "modalities": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
                "endpoints": [ModelEndpointEnum.EMBEDDING],
            }

        # Default fallback for unknown URIs
        return {
            "modalities": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
            "endpoints": [ModelEndpointEnum.CHAT],
        }

    @staticmethod
    async def derive_model_specs(model_data: LiteLLMModelInfo) -> Dict[str, Any]:
        """Determine the modality and endpoints of the model.

        Args:
            provider_data: The provider data
        """
        config = model_data.config

        # Initialize supported modalities
        supported_modalities = []
        supported_model_endpoints = []

        # Modalities come from the capability flags, with the mode as the fallback. ROUTES do
        # not: a flag says what a model accepts or produces, not where it is served. Deriving
        # routes from flags is how an embedding model with `supports_audio_input` was offered
        # at /v1/audio/transcriptions and never at /v1/embeddings, how Sora became a chat
        # model, and how thirteen realtime models gained speech routes they cannot serve --
        # which also defeated the "no route = realtime, hide it" rule budapp relies on.
        input_modalities = config.get("supported_modalities", [])
        for modality in input_modalities:
            if modality == "text":
                supported_modalities.append(ModalityEnum.TEXT_INPUT)
            elif modality == "image":
                supported_modalities.append(ModalityEnum.IMAGE_INPUT)
            elif modality == "audio":
                supported_modalities.append(ModalityEnum.AUDIO_INPUT)

        output_modalities = config.get("supported_output_modalities", [])
        for modality in output_modalities:
            if modality in ("text", "code"):
                supported_modalities.append(ModalityEnum.TEXT_OUTPUT)
            elif modality == "image":
                supported_modalities.append(ModalityEnum.IMAGE_OUTPUT)
            elif modality == "audio":
                supported_modalities.append(ModalityEnum.AUDIO_OUTPUT)

        if config.get("supports_embedding_image_input", False):
            supported_modalities.append(ModalityEnum.IMAGE_INPUT)
        if config.get("supports_audio_input", False):
            supported_modalities.append(ModalityEnum.AUDIO_INPUT)
        # supports_pdf_input / supports_video_input: TODO, enable when budserve supports file input
        if config.get("supports_vision", False):
            supported_modalities.extend([ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT, ModalityEnum.IMAGE_INPUT])
        if config.get("supports_image_input", False):
            supported_modalities.append(ModalityEnum.IMAGE_INPUT)
        if config.get("supports_audio_output", False):
            supported_modalities.append(ModalityEnum.AUDIO_OUTPUT)

        mode = config.get("mode") or ""
        if not supported_modalities:
            supported_modalities = list(MODE_MODALITIES.get(mode, ()))

        supported_model_endpoints = mode_routes(config)

        # Get supported endpoints
        if config.get("supported_endpoints", []):
            # Get supported endpoints from config
            logger.debug("Found supported endpoints in config")
            supported_model_endpoints = []
            for endpoint in config.get("supported_endpoints", []):
                try:
                    route = ENDPOINT_ALIASES.get(endpoint) or ModelEndpointEnum(endpoint)
                except ValueError:
                    # The explicit list is authoritative: it says where the model is SERVED.
                    # Falling back to the mode-derived route here would be wrong -- a model
                    # listed only at /vertex_ai/live cannot be called at /v1/chat/completions,
                    # and advertising that route fails at request time. So the endpoint is
                    # dropped, but loudly: at DEBUG this hid 25 realtime models losing their
                    # only route, which left them in the catalog with none.
                    #
                    # Keeping them with an empty endpoint list is a decision, not a gap
                    # (2026-09-24). budapp hides models whose `endpoints` is empty. An empty
                    # list means "no Bud route serves this": Vertex Live, video generation,
                    # OCR, and audio a voice vendor's gateway cannot dispatch -- so do not
                    # "fix" it with a fallback route. /v1/realtime itself left this set when
                    # FRD-023 gave it a value; `gate_realtime_route` now decides who keeps it.
                    logger.warning(
                        "Model %s is served at %s, which has no ModelEndpointEnum value; "
                        "no Bud route can serve it there",
                        model_data.uri,
                        endpoint,
                    )
                    continue
                if route is ModelEndpointEnum.REALTIME and mode not in REALTIME_MODES:
                    # Not a warning: this is the rule working, every night, for gpt-audio*.
                    logger.info(
                        "Model %s (mode %r) is also listed at %s; it stays on its other routes",
                        model_data.uri,
                        mode,
                        endpoint,
                    )
                    continue
                supported_model_endpoints.append(route)

        if set(supported_model_endpoints) == {ModelEndpointEnum.BATCH}:
            # Batch is a way of calling a route, not a route. Mistral OCR is listed at
            # /v1/ocr and /v1/batch; with /v1/ocr unservable, BATCH alone survived and made the
            # model look deployable -- and kept it out of the "no route" set budapp hides.
            supported_model_endpoints = []

        # Sorted, not list(set(...)). A set's iteration order follows string hashing, which
        # Python randomises per process, and Postgres compares arrays by order -- so the same
        # modalities written by two sync runs could compare as different. That made
        # modified_at move on rows where nothing had changed: observed as 8 rows storing
        # AUDIO_OUTPUT,TEXT_INPUT and 5 storing TEXT_INPUT,AUDIO_OUTPUT for the same set.
        return {
            "modalities": sorted(set(supported_modalities), key=lambda m: m.value),
            "endpoints": sorted(set(supported_model_endpoints), key=lambda e: e.value),
        }


class TensorZeroSeeder(BaseSeeder):
    """Seeder for TensorZero model data.

    This class handles the process of loading TensorZero model data from files
    and preparing it for database insertion.
    """

    # TODO: Remove after confirming SDK-based fetching is stable
    @staticmethod
    async def get_version_file_path(version: str) -> str:
        """Generate a file path for the TensorZero model data file for a specific version.

        Args:
            version: The version string (e.g., "0.1.0")

        Returns:
            Path to the TensorZero model data file

        Raises:
            ValueError: If the version string is invalid
        """
        if not version or not isinstance(version, str):
            raise ValueError("Version must be a non-empty string")

        # Replace periods with underscores in version
        sanitized_version = version.replace(".", "_")

        if not sanitized_version:
            raise ValueError("Version string contains no valid characters after sanitization")

        return os.path.join(TENSORZERO_DATA_DIR, f"tensorzero_v_{sanitized_version}.json")

    @staticmethod
    async def get_parser_by_version(version: str) -> TensorZeroParser:
        """Get the parser for the TensorZero model data based on the version specification.

        Different versions may require different parsing logic.

        Args:
            version: The version string (e.g., "0.1.0")
            file_path: Path to the model data file

        Returns:
            A parser for the TensorZero model data

        Raises:
            ValueError: If the version is not supported
            SeederException: If there is an error parsing the data
        """
        if version in ["0.1.0"]:
            return TensorZeroParser()
        else:
            raise ValueError(f"Unsupported TensorZero version: {version}")

    async def get_license_id_map(self) -> Dict[str, UUID]:
        """Get mapping of license keys to IDs from the database.

        Returns:
            Dict mapping license keys to their database IDs
        """
        license_id_map = {}

        with LicenseCRUD() as license_crud:
            session = license_crud.get_session()
            try:
                # Fetch all licenses from database using direct query
                from ..model.models import License

                licenses = session.query(License).all()
                for license in licenses:
                    license_id_map[license.key] = license.id
                logger.debug("Loaded %d licenses from database", len(license_id_map))
            except Exception as e:
                logger.warning("Failed to load licenses from database: %s", e)
                logger.info("Continuing with empty license mapping - models will have null license_id")

        return license_id_map

    def get_existing_model_uris(self, engine_version_id: UUID) -> Dict[str, UUID]:
        """Get all existing model URIs associated with an engine version.

        Args:
            engine_version_id: The ID of the engine version

        Returns:
            Dict mapping model URIs to their database IDs
        """
        uri_to_id_map: Dict[str, UUID] = {}

        with ModelInfoCRUD() as model_info_crud:
            session = model_info_crud.get_session()
            try:
                # Query models associated with this engine version
                results = (
                    session.query(ModelInfo.uri, ModelInfo.id)
                    .join(
                        engine_version_model_info,
                        ModelInfo.id == engine_version_model_info.c.model_info_id,
                    )
                    .filter(engine_version_model_info.c.engine_version_id == engine_version_id)
                    .all()
                )
                for uri, model_id in results:
                    uri_to_id_map[uri] = model_id
                logger.debug("Found %d existing models for engine version %s", len(uri_to_id_map), engine_version_id)
            except Exception as e:
                logger.warning("Failed to get existing model URIs: %s", e)

        return uri_to_id_map

    def get_existing_provider_types(self, engine_version_id: UUID) -> Dict[str, UUID]:
        """provider_type -> id for every provider currently linked to this engine version.

        The "before" side of retirement: anything here that the catalog no longer defines has
        left, and its association should go.
        """
        with ProviderCRUD() as provider_crud:
            session = provider_crud.get_session()
            rows = (
                session.query(Provider.provider_type, Provider.id)
                .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
                .filter(engine_version_provider.c.engine_version_id == engine_version_id)
                .all()
            )
            return dict(rows)

    def deactivate_stale_providers(self, engine_version_id: UUID, stale_provider_ids: List[UUID]) -> int:
        """Stop serving providers that have left the catalog.

        The counterpart to `deactivate_stale_models`, which providers never had. Without it the
        seeder only ever ADDS: removing an entry from tensorzero_providers.json left the row in
        place, still associated with the engine version, still returned by the API. That is how
        `together` went on being served after it was deleted from the catalog, showing Together
        AI twice in the picker.

        Only the ASSOCIATION is removed, never the provider row. Three foreign keys point at
        `provider` — engine_version_provider, model_info.provider_id and
        guardrail_probe.provider_id (RESTRICT) — so a delete fails whenever anything still
        references it, which is exactly what the API's own delete endpoint runs into. Dropping
        the association is enough: the catalog is served per engine version, so an unassociated
        provider disappears from the response while its history stays intact.

        Args:
            engine_version_id: The engine version to unlink them from
            stale_provider_ids: Providers no longer present in the catalog

        Returns:
            Number of associations removed
        """
        if not stale_provider_ids:
            return 0

        with ProviderCRUD() as provider_crud:
            session = provider_crud.get_session()
            try:
                delete_assoc_stmt = delete(engine_version_provider).where(
                    engine_version_provider.c.engine_version_id == engine_version_id,
                    engine_version_provider.c.provider_id.in_(stale_provider_ids),
                )
                result = session.execute(delete_assoc_stmt)
                session.commit()
                removed = result.rowcount or 0
                logger.info(
                    "Retired %d stale provider association(s) from engine version %s",
                    removed,
                    engine_version_id,
                )
                return removed
            except Exception as e:
                session.rollback()
                logger.error("Failed to retire stale providers: %s", e)
                raise

    def deactivate_stale_models(self, engine_version_id: UUID, stale_model_ids: List[UUID]) -> int:
        """Deactivate models that are no longer in the new model list.

        This method removes the association between models and the engine version,
        and marks the model as inactive if it has no other engine version associations.

        Args:
            engine_version_id: The ID of the engine version
            stale_model_ids: List of model IDs to deactivate

        Returns:
            Number of models deactivated
        """
        if not stale_model_ids:
            return 0

        deactivated_count = 0

        with ModelInfoCRUD() as model_info_crud:
            session = model_info_crud.get_session()
            try:
                # First, remove the association from engine_version_model_info
                delete_assoc_stmt = delete(engine_version_model_info).where(
                    engine_version_model_info.c.engine_version_id == engine_version_id,
                    engine_version_model_info.c.model_info_id.in_(stale_model_ids),
                )
                session.execute(delete_assoc_stmt)

                # Then, mark models with no remaining associations as inactive
                for model_id in stale_model_ids:
                    other_assoc = (
                        session.query(engine_version_model_info)
                        .filter(engine_version_model_info.c.model_info_id == model_id)
                        .first()
                    )
                    if not other_assoc:
                        session.query(ModelInfo).filter(ModelInfo.id == model_id).update(
                            {"status": ModelStatusEnum.INACTIVE}
                        )
                        deactivated_count += 1

                session.commit()
                logger.info(
                    "Deactivated %d stale models, removed %d associations",
                    deactivated_count,
                    len(stale_model_ids),
                )
            except Exception as e:
                session.rollback()
                logger.error("Failed to deactivate stale models: %s", e)
                raise

        return deactivated_count

    async def seed(self) -> None:
        """Seed the database with TensorZero model data.

        This method:
        1. Seeds license records
        2. Loads the engine configuration
        3. Identifies TensorZero engine versions
        4. Processes each version's model data
        5. Prepares data for database insertion

        Raises:
            SeederException: If there is an error during the seeding process
        """
        try:
            # Get license ID mapping from database (assumes LicenseSeeder has already run)
            license_id_map = await self.get_license_id_map()
            if not license_id_map:
                logger.warning("No licenses found in database. Run LicenseSeeder first.")
                # Continue anyway - models will have null license_id
            # Load TensorZero engine configuration from database
            engine_crud = EngineCRUD()
            with engine_crud as crud, crud.get_session() as session:
                db_engine = engine_crud.fetch_one(conditions={"name": "tensorzero"}, session=session)
                if not db_engine:
                    logger.warning("No TensorZero engine found")
                    return

                if not db_engine.versions:
                    logger.warning("No versions defined for TensorZero engine")
                    return

            # Set when the SDK's fetch could not be trusted for some version: that version gets the
            # curated decision models only, and the sync still fails once every version is done.
            untrusted: Optional[UntrustedCatalogError] = None

            # Process each version
            for version_config in db_engine.versions:
                version = version_config.version
                if not version:
                    logger.warning("Skipping invalid version configuration: missing version number")
                    continue

                logger.debug("Processing TensorZero version: %s", version)

                # Providers linked to this version BEFORE this run, and the ones this run
                # upserts. The difference is what has left the catalog.
                existing_providers = self.get_existing_provider_types(version_config.id)
                seeded_provider_types: Set[str] = set()

                # Get existing model URIs for this engine version (for cleanup later)
                existing_models = self.get_existing_model_uris(version_config.id)
                logger.debug("Found %d existing models for version %s", len(existing_models), version)

                # Track all new URIs being processed
                processed_uris: Set[str] = set()

                # TODO: (Remove it after testing) Old file-based path validation (replaced by catalog SDK):
                data_file_path = await self.get_version_file_path(version)
                if not os.path.exists(data_file_path):
                    raise SeederException(f"TensorZero data file not found for version {version}: {data_file_path}")

                # Parse model data from catalog SDK
                tensorzero_parser = await self.get_parser_by_version(version)
                try:
                    model_data = await tensorzero_parser.parse_model_data()
                    retire = True
                except UntrustedCatalogError as exc:
                    # The curated decision models are our own file, validated on load, so they can
                    # be applied without the SDK. Additively only: nothing below may read this
                    # run's absences as retirements, because the run never saw the real catalog.
                    untrusted = untrusted or exc
                    model_data = await tensorzero_parser.parse_curated_decision_models()
                    retire = False

                # Read providers data
                predefined_providers = read_json_file(TENSORZERO_PROVIDERS_PATH)
                logger.debug("Predefined providers: %s", len(predefined_providers))

                # NOTE: Adding default huggingface and guardrail providers.
                # Providers listed here carry no catalog models, so the model_data loop below
                # never reaches them - without this list they would never be inserted at all.
                #
                # Most voice providers (FRD-018) are in exactly that position: they have no
                # LiteLLM catalog models because WaaV, not TensorZero, serves them. Omitting one
                # here is a SILENT no-op - the entry sits in tensorzero_providers.json, the
                # seeder runs green, and the provider simply never appears in budadmin.
                #
                # A few of them do carry catalog models now and so are upserted twice, once here
                # and once in the model_data loop below. That is harmless - upsert keys on
                # `provider_type` - and `openai` has always worked that way. See
                # `NO_MODEL_PROVIDERS` in seeders/constants.py for which, and why they stay.
                # `tests/test_voice_providers.py::test_every_no_model_provider_is_seeded` is the
                # guard.
                for provider_type in NO_MODEL_PROVIDERS:
                    provider_data = ProviderCreate(
                        name=predefined_providers[provider_type]["name"],
                        provider_type=provider_type,
                        icon=predefined_providers[provider_type]["icon"],
                        description=predefined_providers[provider_type]["description"],
                        credentials=predefined_providers[provider_type]["credentials"],
                        capabilities=predefined_providers[provider_type]["capabilities"],
                    )

                    # Upsert provider
                    with ProviderCRUD() as provider_crud:
                        db_provider_id = provider_crud.upsert(
                            data=provider_data.model_dump(), conflict_target=["provider_type"]
                        )
                        logger.debug("Upserted provider: %s", db_provider_id)
                        provider_crud.add_engine_version(db_provider_id, version_config.id)
                        seeded_provider_types.add(provider_type)

                # Prepare data for database insertion
                for provider, supported_models in model_data.items():
                    provider_data = ProviderCreate(
                        name=predefined_providers[provider]["name"],
                        provider_type=provider,
                        icon=predefined_providers[provider]["icon"],
                        description=predefined_providers[provider]["description"],
                        credentials=predefined_providers[provider]["credentials"],
                        capabilities=predefined_providers[provider]["capabilities"],
                    )

                    # Upsert provider
                    with ProviderCRUD() as provider_crud:
                        db_provider_id = provider_crud.upsert(
                            data=provider_data.model_dump(), conflict_target=["provider_type"]
                        )
                        logger.debug("Upserted provider: %s", db_provider_id)
                        provider_crud.add_engine_version(db_provider_id, version_config.id)
                        seeded_provider_types.add(provider)

                    # Parse model info
                    for model in supported_models:
                        # Get license ID from model data directly, or fall back to mapping
                        license_key = model.config.get("license_id")
                        if not license_key:
                            license_key = get_license_key_for_model(model.uri, provider)
                        license_id = license_id_map.get(license_key) if license_key else None

                        model_info_data = await tensorzero_parser.create_model_info(
                            model, db_provider_id, provider, license_id
                        )

                        # Track the URI being processed
                        processed_uris.add(model_info_data.uri)

                        # Upsert model info
                        with ModelInfoCRUD() as model_info_crud:
                            db_model_info_id = model_info_crud.upsert(
                                data=model_info_data.model_dump(),
                                conflict_target=["uri"],
                            )
                            logger.debug("Upserted model info: %s", db_model_info_id)
                            model_info_crud.add_engine_version(db_model_info_id, version_config.id)

                        # A curated model's description, pros, cons and links (`curated_details_row`).
                        # Only the columns the block owns are written, keyed on the row just upserted.
                        details = model.config.get("details")
                        if details:
                            with ModelDetailsCRUD() as model_details_crud:
                                model_details_crud.upsert(
                                    data={"model_info_id": db_model_info_id, **details},
                                    conflict_target=["model_info_id"],
                                )

                if not retire:
                    logger.warning(
                        "Catalog SDK fetch untrusted for version %s (%s); upserted %d curated decision "
                        "models and retired nothing",
                        version,
                        untrusted,
                        len(processed_uris),
                    )
                    continue

                # Providers that were in the catalog on a previous run and are not now.
                # Collected from the same two loops that upsert them, so the set cannot drift
                # from what was actually seeded.
                stale_provider_ids = [
                    pid for ptype, pid in existing_providers.items() if ptype not in seeded_provider_types
                ]
                if stale_provider_ids:
                    logger.info(
                        "Found %d provider(s) no longer in the catalog for version %s",
                        len(stale_provider_ids),
                        version,
                    )
                    self.deactivate_stale_providers(version_config.id, stale_provider_ids)

                # After processing all models, deactivate stale models
                stale_uris = set(existing_models.keys()) - processed_uris
                refuse_mass_retirement(version, stale_uris, len(existing_models))
                if stale_uris:
                    stale_model_ids = [existing_models[uri] for uri in stale_uris]
                    logger.info("Found %d stale models to deactivate for version %s", len(stale_model_ids), version)
                    self.deactivate_stale_models(version_config.id, stale_model_ids)
                else:
                    logger.debug("No stale models to deactivate for version %s", version)

            if untrusted is not None:
                raise untrusted

        except SeederException:
            # Already says what went wrong -- the catalog guards above depend on their message
            # reaching the cron response. The generic handler below would replace it with
            # "Unexpected error", since SeederException is an Exception subclass.
            raise
        except FileNotFoundError as e:
            logger.exception("File not found during TensorZero seeding: %s", e)
            raise SeederException("File not found during TensorZero seeding") from e
        except json.JSONDecodeError as e:
            logger.exception("JSON decoding error during TensorZero seeding: %s", e)
            raise SeederException("JSON decoding error during TensorZero seeding") from e
        except ValueError as e:
            logger.exception("Value error during TensorZero seeding: %s", e)
            raise SeederException("Value error during TensorZero seeding") from e
        except Exception as e:
            logger.exception("Unexpected error during TensorZero seeding: %s", e)
            raise SeederException("Unexpected error during TensorZero seeding") from e


if __name__ == "__main__":
    import asyncio

    asyncio.run(TensorZeroSeeder().seed())


# python -m budconnect.seeders.tensorzero
