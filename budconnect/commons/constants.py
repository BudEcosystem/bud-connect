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
    """

    MODEL = "model"
    MODERATION = "moderation"
    LOCAL = "local"


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


class ScannerTypeEnum(str, Enum):
    """Type of model scanner for guardrail rules.

    Attributes:
        CLASSIFIER: Classification model (e.g., Arch-Guard).
        LLM: LLM-based policy scanner.
        PATTERN: Pattern-based detection (regex, keywords).
        STATIC_CLASSIFIER: Static/rule-based classifier.
    """

    CLASSIFIER = "classifier"
    LLM = "llm"
    PATTERN = "pattern"
    STATIC_CLASSIFIER = "static_classifier"
