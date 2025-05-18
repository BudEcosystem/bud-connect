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

"""The model schemas, containing essential data structures for the model microservice."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from budmicroframe.commons.schemas import PaginatedResponse
from pydantic import UUID4, BaseModel, ConfigDict, Field

from ..commons.constants import ModalityEnum, ModelEndpointEnum


class LiteLLMModelInfo(BaseModel):
    """Schema for LiteLLM model seeder."""

    uri: str
    config: Dict[str, Any]


class ProviderCreate(BaseModel):
    """Schema for provider creation."""

    name: str
    provider_type: str
    icon: str
    description: str


class InputCost(BaseModel):
    """Validates input cost configuration for model pricing."""

    input_cost_per_audio_per_second: Optional[float] = Field(None)
    input_cost_per_video_per_second_above_8s_interval: Optional[float] = Field(None)
    input_cost_per_image: Optional[float] = Field(None)
    input_cost_per_token_batch_requests: Optional[float] = Field(None)
    input_cost_per_audio_per_second_above_128k_tokens: Optional[float] = Field(None)
    input_cost_per_token_cache_hit: Optional[float] = Field(None)
    input_cost_per_video_per_second_above_15s_interval: Optional[float] = Field(None)
    input_cost_per_video_per_second: Optional[float] = Field(None)
    input_cost_per_token_batches: Optional[float] = Field(None)
    input_cost_per_pixel: Optional[float] = Field(None)
    input_cost_per_token_above_200k_tokens: Optional[float] = Field(None)
    input_cost_per_video_per_second_above_128k_tokens: Optional[float] = Field(None)
    input_cost_per_character: Optional[float] = Field(None)
    input_cost_per_image_above_128k_tokens: Optional[float] = Field(None)
    input_cost_per_token_above_128k_tokens: Optional[float] = Field(None)
    input_cost_per_query: Optional[float] = Field(None)
    input_cost_per_audio_token: Optional[float] = Field(None)
    input_cost_per_token: Optional[float] = Field(None)
    input_cost_per_request: Optional[float] = Field(None)
    input_cost_per_second: Optional[float] = Field(None)
    input_cost_per_character_above_128k_tokens: Optional[float] = Field(None)
    input_dbu_cost_per_token: Optional[float] = Field(None)

    class Config:
        """Config for input cost."""

        extra = "forbid"


class OutputCost(BaseModel):
    """Validates output cost configuration for model pricing."""

    output_cost_per_pixel: Optional[float] = Field(None)
    output_cost_per_token: Optional[float] = Field(None)
    output_cost_per_character: Optional[float] = Field(None)
    output_dbu_cost_per_token: Optional[float] = Field(None)
    output_cost_per_image: Optional[float] = Field(None)
    output_cost_per_token_above_200k_tokens: Optional[float] = Field(None)
    output_cost_per_character_above_128k_tokens: Optional[float] = Field(None)
    output_cost_per_second: Optional[float] = Field(None)
    output_cost_per_audio_token: Optional[float] = Field(None)
    output_cost_per_token_batches: Optional[float] = Field(None)
    output_cost_per_token_above_128k_tokens: Optional[float] = Field(None)
    output_cost_per_reasoning_token: Optional[float] = Field(None)
    output_db_cost_per_token: Optional[float] = Field(None)

    class Config:
        """Config for output cost."""

        extra = "forbid"


class CacheCost(BaseModel):
    """Validates cache cost configuration for model pricing."""

    cache_read_input_token_cost: Optional[float] = Field(None)
    cache_read_input_audio_token_cost: Optional[float] = Field(None)
    cache_creation_input_audio_token_cost: Optional[float] = Field(None)
    cache_creation_input_token_cost: Optional[float] = Field(None)

    class Config:
        """Config for cache cost."""

        extra = "forbid"


class SearchContextCost(BaseModel):
    """Validates search context cost configuration."""

    search_context_size_low: Optional[float] = Field(None)
    search_context_size_medium: Optional[float] = Field(None)
    search_context_size_high: Optional[float] = Field(None)

    class Config:
        """Config for search context cost."""

        extra = "forbid"


class Tokens(BaseModel):
    """Validates token limits configuration."""

    max_input_tokens: Optional[int] = Field(None)
    max_tokens_per_document_chunk: Optional[int] = Field(None)
    max_query_tokens: Optional[int] = Field(None)
    max_output_tokens: Optional[int] = Field(None)
    max_tokens: Optional[int] = Field(None)
    tool_use_system_prompt_tokens: Optional[int] = Field(None)

    class Config:
        """Config for tokens."""

        extra = "forbid"


class RateLimits(BaseModel):
    """Validates rate limits configuration."""

    rpd: Optional[int] = Field(None)
    tpm: Optional[int] = Field(None)
    rpm: Optional[int] = Field(None)

    class Config:
        """Config for rate limits."""

        extra = "forbid"


class MediaLimits(BaseModel):
    """Validates media limits configuration."""

    max_audio_per_prompt: Optional[int] = Field(None)
    max_document_chunks_per_query: Optional[int] = Field(None)
    max_audio_length_hours: Optional[float] = Field(None)
    max_images_per_prompt: Optional[int] = Field(None)
    max_videos_per_prompt: Optional[int] = Field(None)
    max_pdf_size_mb: Optional[float] = Field(None)
    max_video_length: Optional[float] = Field(None)

    class Config:
        """Config for media limits."""

        extra = "forbid"


class Features(BaseModel):
    """Validates model features configuration."""

    supports_web_search: Optional[bool] = Field(None)
    supports_response_schema: Optional[bool] = Field(None)
    supports_reasoning: Optional[bool] = Field(None)
    supports_system_messages: Optional[bool] = Field(None)
    supports_tool_choice: Optional[bool] = Field(None)
    supports_parallel_function_calling: Optional[bool] = Field(None)
    supports_assistant_prefill: Optional[bool] = Field(None)
    supports_function_calling: Optional[bool] = Field(None)
    supports_native_streaming: Optional[bool] = Field(None)
    supports_prompt_caching: Optional[bool] = Field(None)

    class Config:
        """Config for features."""

        extra = "forbid"


class ModelInfoCreate(BaseModel):
    """Schema for model info creation."""

    uri: str
    modality: List[ModalityEnum]
    provider_id: UUID4
    input_cost: Optional[InputCost] = None
    output_cost: Optional[OutputCost] = None
    cache_cost: Optional[CacheCost] = None
    search_context_cost_per_query: Optional[SearchContextCost] = None
    tokens: Optional[Tokens] = None
    rate_limits: Optional[RateLimits] = None
    media_limits: Optional[MediaLimits] = None
    features: Optional[Features] = None
    endpoints: List[ModelEndpointEnum]
    deprecation_date: Optional[datetime] = None

    def model_dump(self, **kwargs):
        """Implement custom model_dump to convert nested Pydantic models to None."""
        # Get the base dump with all fields
        data = super().model_dump(**kwargs)

        # Process nested Pydantic models to exclude nulls
        nested_fields = [
            "input_cost",
            "output_cost",
            "cache_cost",
            "search_context_cost_per_query",
            "tokens",
            "rate_limits",
            "media_limits",
            "features",
        ]

        for field in nested_fields:
            if data[field] is not None:
                # Dump nested models with exclude_none=True
                nested_data = getattr(self, field).model_dump(exclude_none=True)
                # Only include the field if it has non-null values
                data[field] = nested_data if nested_data else None

        return data


# Api Schemas


class ModelInfoResponse(BaseModel):
    """Schema for model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    uri: str
    modality: List[ModalityEnum]
    provider_id: UUID4
    input_cost: Optional[dict] = None
    output_cost: Optional[dict] = None
    cache_cost: Optional[dict] = None
    search_context_cost_per_query: Optional[dict] = None
    tokens: Optional[dict] = None
    rate_limits: Optional[dict] = None
    media_limits: Optional[dict] = None
    features: Optional[dict] = None
    endpoints: List[ModelEndpointEnum]
    deprecation_date: Optional[datetime] = None


class CompatibleProviders(ProviderCreate):
    """Schema for compatible providers."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    models: List[ModelInfoResponse] = []


class CompatibleModelsResponse(PaginatedResponse):
    """Schema for compatible models response."""

    model_config = ConfigDict(from_attributes=True)

    engine_name: str
    engine_version: Optional[str] = None
    items: List[CompatibleProviders]
