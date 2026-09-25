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

"""The constants used in the budconnect module."""

from enum import Enum


class ModalityEnum(Enum):
    """Enumeration of model modalities.

    This enum represents different types of AI model modalities or capabilities.

    Attributes:
        TEXT_INPUT (str): Represents text input modality.
        TEXT_OUTPUT (str): Represents text output modality.
        IMAGE_INPUT (str): Represents image input modality.
        IMAGE_OUTPUT (str): Represents image output modality.
        AUDIO_INPUT (str): Represents audio input modality.
        AUDIO_OUTPUT (str): Represents audio output modality.
    """

    TEXT_INPUT = "text_input"
    TEXT_OUTPUT = "text_output"
    IMAGE_INPUT = "image_input"
    IMAGE_OUTPUT = "image_output"
    AUDIO_INPUT = "audio_input"
    AUDIO_OUTPUT = "audio_output"


class ModelEndpointEnum(Enum):
    """Enumeration of API endpoints for different model capabilities.

    This enum represents the different API endpoints that can be used to access
    various AI model functionalities.

    Attributes:
        CHAT (str): Chat completion endpoint for conversational AI.
        COMPLETION (str): Text completion endpoint for non-conversational AI.
        IMAGE_GENERATION (str): Image creation endpoint.
        IMAGE_EDIT (str): Image editing endpoint.
        IMAGE_VARIATION (str): Image variation generation endpoint.
        AUDIO_TRANSCRIPTION (str): Speech-to-text conversion endpoint.
        AUDIO_TRANSLATION (str): Audio translation endpoint.
        AUDIO_SPEECH (str): Text-to-speech synthesis endpoint.
        EMBEDDING (str): Vector embedding generation endpoint.
        BATCH (str): Batch processing endpoint for multiple requests.
        RESPONSE (str): Response retrieval endpoint for asynchronous operations.
        DOCUMENT (str): Document processing endpoint.
        RERANK (str): Reranking endpoint for search results.
        MODERATION (str): Content moderation endpoint.
    """

    CHAT = "/v1/chat/completions"
    COMPLETION = "/v1/completions"
    IMAGE_GENERATION = "/v1/images/generations"
    IMAGE_EDIT = "/v1/images/edits"
    IMAGE_VARIATION = "/v1/images/variations"
    AUDIO_TRANSCRIPTION = "/v1/audio/transcriptions"
    AUDIO_TRANSLATION = "/v1/audio/translations"
    AUDIO_SPEECH = "/v1/audio/speech"
    EMBEDDING = "/v1/embeddings"
    BATCH = "/v1/batch"
    RESPONSE = "/v1/responses"
    DOCUMENT = "/v1/documents"
    RERANK = "/v1/rerank"  # https://docs.litellm.ai/docs/rerank
    MODERATION = "/v1/moderations"  # https://docs.litellm.ai/docs/moderation


class ProviderCapabilityEnum(Enum):
    """Enumeration for identifying provider capabilities.

    This enum categorizes providers like OpenAI, Azure, and AWS Bedrock based on
    the specific services they offer, allowing for clear differentiation between
    their core functionalities.

    Attributes:
        MODEL: Represents providers that support model hubs or offer direct access
               to model inference endpoints.
        MODERATION: Represents providers that offer content moderation, safety, or
                    guardrail endpoints.
        LOCAL: Represents providers that expose local or user-managed runtimes.
        TEXT_TO_SPEECH: The provider can synthesise speech through the audio gateway.
        AUDIO_TRANSCRIPTION: The provider can transcribe audio through the audio gateway.
        AUDIO_TRANSLATION: The provider can translate audio to English text.

    The first three say what KIND of provider this is; the audio three say what it can serve.
    They share one array on purpose -- "what can this provider do" is one question, and budapp
    already filters providers on this field. A voice vendor keeps ``MODEL`` alongside them:
    ``/model/get-compatible-models`` only returns providers carrying MODEL, and budadmin's
    provider picker filters on ``capabilities=model``.

    Values must stay identical to budapp's ``ProviderCapabilityEnum`` -- the wire carries the
    lowercase ``.value``, and budapp validates every incoming string against its own enum,
    aborting the entire catalog sync on one it does not know.
    """

    MODEL = "model"
    MODERATION = "moderation"
    LOCAL = "local"
    TEXT_TO_SPEECH = "text_to_speech"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_TRANSLATION = "audio_translation"


class ModelProviderTypeEnum(str, Enum):
    """Enumeration of model provider types.

    This enum represents different types of model providers or sources.

    Attributes:
        CLOUD_MODEL (str): Represents cloud-based model providers.
        HUGGING_FACE (str): Represents models from the Hugging Face platform.
        URL (str): Represents models accessible via a URL.
        DISK (str): Represents locally stored models on disk.
    """

    CLOUD_MODEL = "cloud_model"
    HUGGING_FACE = "hugging_face"
    URL = "url"
    DISK = "disk"


class ModelStatusEnum(str, Enum):
    """Status of a model in the system."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class ScannerTypeEnum(str, Enum):
    """Type of model scanner for guardrail rules.

    Attributes:
        CLASSIFIER: Classification model (e.g., Arch-Guard).
        LLM: LLM-based policy scanner.
        PATTERN: Pattern-based detection (regex, keywords).
        BUD_RAA_CLASSIFIER: Bud RAA (resource aware attention) classifier.
        AGENTMESH_POLICY: Agent-governance policy (bud-sentinel agentmesh engine);
            a model-less rule whose body is a governance policy, not a scanner model.
    """

    CLASSIFIER = "classifier"
    LLM = "llm"
    PATTERN = "pattern"
    BUD_RAA_CLASSIFIER = "bud_raa_classifier"
    AGENTMESH_POLICY = "agentmesh_policy"


class BillingUnitEnum(str, Enum):
    """The unit a published rate is quoted per.

    The rate alone does not say what to multiply it by. A vendor charging "$0.10 per 1K
    characters" and one charging "$0.22 per hour" are both a single float in
    ``input_cost``, and only this field distinguishes them.

    Attributes:
        SECOND: Per second of audio. The canonical unit for transcription.
        CHARACTER: Per character of input text. The canonical unit for synthesis.
        TOKEN: Per token, text or audio.
        REQUEST: A flat charge per API call, regardless of size.
        IMAGE: Per generated image.
        PIXEL: Per output pixel.

    Rates quoted per minute or per hour are normalised to ``SECOND``, and per-1K-character
    rates to ``CHARACTER``, when the catalog is built. Storing the vendor's display unit
    would make every consumer repeat the conversion, and they would not all repeat it the
    same way.
    """

    SECOND = "second"
    CHARACTER = "character"
    TOKEN = "token"
    REQUEST = "request"
    IMAGE = "image"
    PIXEL = "pixel"


class PriceConfidenceEnum(str, Enum):
    """How much weight a consumer may put on a rate.

    This exists because "no price" and "free" are the same value in a nullable float
    column, and billing a customer zero because nobody could find a price is a silent,
    expensive failure.

    Attributes:
        AUTHORITATIVE: Read from the vendor's own machine-readable price feed (AWS Price
            List, Azure Retail Prices, GCP Billing Catalog). Safe to bill from.
        CURATED: Transcribed by hand from the vendor's published pricing page, with the
            URL and the date it was read recorded in ``BillingSource``. Safe to bill from
            until it goes stale; ``checked_on`` is what says whether it has.
        DERIVED: Computed from something that is not a per-unit price -- a credit
            allowance, a subscription tier, a bundled minute quota. The arithmetic is an
            assumption about how the vendor converts, and it breaks whenever they reprice.
            Show it, flag it, do not invoice from it unsupervised.
        UNKNOWN: No rate could be obtained. Carries no number at all. A consumer MUST
            surface this rather than treating the absent rate as zero.
    """

    AUTHORITATIVE = "authoritative"
    CURATED = "curated"
    DERIVED = "derived"
    UNKNOWN = "unknown"
