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

from ..commons.constants import ModalityEnum, ModelEndpointEnum, ProviderCapabilityEnum


class LicenseFAQ(BaseModel):
    """Schema for license FAQ item."""

    question: str
    answer: str
    reason: List[str]
    impact: str


class LicenseCreate(BaseModel):
    """Schema for creating a license."""

    key: str
    name: str
    type: str
    type_description: str
    type_suitability: str
    faqs: List[LicenseFAQ]


class LicenseResponse(BaseModel):
    """Schema for license response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    key: str
    name: str
    type: str
    type_description: str
    type_suitability: str
    faqs: List[LicenseFAQ]
    created_at: datetime
    modified_at: datetime


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
    credentials: List[Dict[str, Any]]
    capabilities: List[ProviderCapabilityEnum]


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
        """Configuration for input cost validation."""

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
        """Configuration for output cost validation."""

        extra = "forbid"


class CacheCost(BaseModel):
    """Validates cache cost configuration for model pricing."""

    cache_read_input_token_cost: Optional[float] = Field(None)
    cache_read_input_audio_token_cost: Optional[float] = Field(None)
    cache_creation_input_audio_token_cost: Optional[float] = Field(None)
    cache_creation_input_token_cost: Optional[float] = Field(None)

    class Config:
        """Configuration for cache cost validation."""

        extra = "forbid"


class SearchContextCost(BaseModel):
    """Validates search context cost configuration."""

    search_context_size_low: Optional[float] = Field(None)
    search_context_size_medium: Optional[float] = Field(None)
    search_context_size_high: Optional[float] = Field(None)

    class Config:
        """Configuration for search context cost validation."""

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
        """Configuration for token limits validation."""

        extra = "forbid"


class RateLimits(BaseModel):
    """Validates rate limits configuration."""

    rpd: Optional[int] = Field(None)
    tpm: Optional[int] = Field(None)
    rpm: Optional[int] = Field(None)

    class Config:
        """Configuration for rate limits validation."""

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
        """Configuration for media limits validation."""

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
        """Configuration for features validation."""

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
    license_id: Optional[UUID4] = None
    model_architecture_class_id: Optional[UUID4] = None
    chat_template: Optional[str] = None
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_type: Optional[str] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
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


class ModelInfoUpdate(BaseModel):
    """Schema for updating model info."""

    uri: Optional[str] = None
    modality: Optional[List[ModalityEnum]] = None
    provider_id: Optional[UUID4] = None
    input_cost: Optional[InputCost] = None
    output_cost: Optional[OutputCost] = None
    cache_cost: Optional[CacheCost] = None
    search_context_cost_per_query: Optional[SearchContextCost] = None
    tokens: Optional[Tokens] = None
    rate_limits: Optional[RateLimits] = None
    media_limits: Optional[MediaLimits] = None
    features: Optional[Features] = None
    endpoints: Optional[List[ModelEndpointEnum]] = None
    deprecation_date: Optional[datetime] = None
    license_id: Optional[UUID4] = None
    model_architecture_class_id: Optional[UUID4] = None
    chat_template: Optional[str] = None
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_type: Optional[str] = None


# Api Schemas


class ModelArchitectureClassBase(BaseModel):
    """Base schema for model architecture class."""

    class_name: str
    architecture_family: str
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_type: Optional[str] = None
    supports_lora: bool = False
    supports_pipeline_parallelism: bool = False


class ModelArchitectureClassCreate(ModelArchitectureClassBase):
    """Schema for creating a model architecture class."""

    pass


class ModelArchitectureClassUpdate(BaseModel):
    """Schema for updating a model architecture class."""

    architecture_family: Optional[str] = None
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_type: Optional[str] = None
    supports_lora: Optional[bool] = None
    supports_pipeline_parallelism: Optional[bool] = None


class ModelArchitectureClassResponse(ModelArchitectureClassBase):
    """Schema for model architecture class response."""

    id: UUID4
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelInfoResponse(BaseModel):
    """Schema for model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    uri: str
    modality: List[ModalityEnum]
    provider_id: UUID4
    provider_name: Optional[str] = None
    provider_type: Optional[str] = None
    input_cost: Optional[Dict[str, Any]] = None
    output_cost: Optional[Dict[str, Any]] = None
    cache_cost: Optional[Dict[str, Any]] = None
    search_context_cost_per_query: Optional[Dict[str, Any]] = None
    tokens: Optional[Dict[str, Any]] = None
    rate_limits: Optional[Dict[str, Any]] = None
    media_limits: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None
    endpoints: List[ModelEndpointEnum]
    deprecation_date: Optional[datetime] = None
    license: Optional[LicenseResponse] = None
    architecture_class: Optional[ModelArchitectureClassResponse] = None
    chat_template: Optional[str] = None
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_type: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None


class ModelListResponse(BaseModel):
    """Response schema for model list with pagination."""

    models: List[ModelInfoResponse]
    total: int
    page: int
    page_size: int


class CompatibleProviders(ProviderCreate):
    """Schema for compatible providers."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    models: List[ModelInfoResponse] = []


class CompatibleModelsResponse(PaginatedResponse[CompatibleProviders]):
    """Schema for compatible models response."""

    model_config = ConfigDict(from_attributes=True)

    engine_name: Optional[str] = None
    engine_version: Optional[str] = None
    items: List[CompatibleProviders]


class ModelEvaluation(BaseModel):
    """Schema for model evaluation scores."""

    name: str = Field(..., description="Name of the evaluation benchmark")
    score: float = Field(..., description="Score achieved on the benchmark")


class ModelPaper(BaseModel):
    """Schema for model-related research papers."""

    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    url: Optional[str] = Field(None, description="URL to the paper")


class ModelDetailsUpdate(BaseModel):
    """Schema for updating model details."""

    description: Optional[str] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    # Pricing & Limits
    input_cost: Optional[InputCost] = None
    output_cost: Optional[OutputCost] = None
    cache_cost: Optional[CacheCost] = None
    search_context_cost_per_query: Optional[SearchContextCost] = None
    tokens: Optional[Tokens] = None
    rate_limits: Optional[RateLimits] = None
    media_limits: Optional[MediaLimits] = None

    # Features
    features: Optional[Features] = None


class ModelDetailsResponse(BaseModel):
    """Schema for model details response with model info and provider."""

    model_config = ConfigDict(from_attributes=True)

    # ModelDetails fields
    id: UUID4
    model_info_id: UUID4
    description: Optional[str] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    evaluations: Optional[List[ModelEvaluation]] = None
    languages: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    tasks: Optional[List[str]] = None
    papers: Optional[List[ModelPaper]] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    architecture: Optional[Dict[str, Any]] = None
    model_tree: Optional[Dict[str, Any]] = None
    extraction_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    modified_at: datetime

    # ModelInfo fields
    uri: str
    modality: Optional[List[ModalityEnum]] = None
    input_cost: Optional[Dict[str, Any]] = None
    output_cost: Optional[Dict[str, Any]] = None
    cache_cost: Optional[Dict[str, Any]] = None
    search_context_cost_per_query: Optional[Dict[str, Any]] = None
    tokens: Optional[Dict[str, Any]] = None
    rate_limits: Optional[Dict[str, Any]] = None
    media_limits: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None
    endpoints: Optional[List[ModelEndpointEnum]] = None
    deprecation_date: Optional[datetime] = None
    license: Optional[LicenseResponse] = None
    architecture_class: Optional[ModelArchitectureClassResponse] = None
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_type: Optional[str] = None

    # Provider fields
    provider_name: str
    provider_type: str


class ModelCapabilityBase(BaseModel):
    """Base schema for model capability."""

    model_info_id: UUID4
    engine_version_id: UUID4
    tool_calling_enabled: bool = False
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_enabled: bool = False
    reasoning_parser_type: Optional[str] = None
    compatibility_notes: Optional[Dict[str, Any]] = None


class ModelCapabilityCreate(ModelCapabilityBase):
    """Schema for creating a model capability."""

    pass


class ModelCapabilityUpdate(BaseModel):
    """Schema for updating a model capability."""

    tool_calling_enabled: Optional[bool] = None
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_enabled: Optional[bool] = None
    reasoning_parser_type: Optional[str] = None
    compatibility_notes: Optional[Dict[str, Any]] = None


class ModelCapabilityResponse(ModelCapabilityBase):
    """Schema for model capability response."""

    id: UUID4
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)
