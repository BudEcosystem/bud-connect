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

"""Guardrail Pydantic schemas for API validation and serialization."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from budmicroframe.commons.schemas import PaginatedResponse
from pydantic import UUID4, BaseModel, ConfigDict, model_validator

from ..commons.constants import ModelProviderTypeEnum, ProviderCapabilityEnum, ScannerTypeEnum


class ProviderCreate(BaseModel):
    """Schema for provider creation."""

    name: str
    provider_type: str
    icon: str
    description: str
    credentials: List[Dict[str, Any]]
    capabilities: list[ProviderCapabilityEnum]


class GuardrailProbeCreate(BaseModel):
    name: str
    uri: str
    provider_id: UUID4
    description: Optional[str] = None
    icon: Optional[str] = None
    tags: Optional[list[str]] = None
    deprecation_date: Optional[datetime] = None


class GuardrailRuleCreate(BaseModel):
    name: str
    uri: str
    probe_id: UUID4
    description: Optional[str] = None
    icon: Optional[str] = None
    deprecation_date: Optional[datetime] = None
    examples: Optional[List[str]] = None
    scanner_type: Optional[ScannerTypeEnum] = None
    modality_types: Optional[List[str]] = None
    guard_types: Optional[List[str]] = None
    model_id: Optional[str] = None
    model_provider_type: Optional[ModelProviderTypeEnum] = None
    is_gated: Optional[bool] = None

    @model_validator(mode="after")
    def validate_model_fields(self) -> "GuardrailRuleCreate":
        """Validate that model_provider_type and is_gated are present when model_id is set."""
        if self.model_id is not None:
            if self.model_provider_type is None:
                raise ValueError("model_provider_type is required when model_id is present")
            if self.is_gated is None:
                raise ValueError("is_gated is required when model_id is present")
        return self


class GuardrailProbeResponse(GuardrailProbeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    examples: Optional[list[str]] = None
    guard_types: Optional[List[str]] = None
    scanner_types: Optional[List[str]] = None
    modality_types: Optional[List[str]] = None
    rules_count: int = 0


class CompatibleProviders(ProviderCreate):
    """Schema for compatible providers."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    probes: List[GuardrailProbeResponse] = []


class CompatibleProbesResponse(PaginatedResponse):
    """Schema for compatible probes response."""

    model_config = ConfigDict(from_attributes=True)

    engine_name: str
    engine_version: Optional[str] = None
    items: List[CompatibleProviders]


class RuleDetail(BaseModel):
    """Schema for individual rule details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    uri: str
    description: Optional[str] = None
    icon: Optional[str] = None
    examples: Optional[List[str]] = None
    deprecation_date: Optional[datetime] = None
    guard_types: Optional[List[str]] = None
    scanner_type: Optional[ScannerTypeEnum] = None
    modality_types: Optional[List[str]] = None
    model_id: Optional[str] = None
    model_provider_type: Optional[ModelProviderTypeEnum] = None
    is_gated: Optional[bool] = None
    created_at: datetime
    modified_at: datetime


class GuardrailRuleResponse(PaginatedResponse):
    """Schema for guardrail rule responses with probe and provider details."""

    model_config = ConfigDict(from_attributes=True)

    # Probe fields
    id: UUID4
    name: str
    uri: str
    description: Optional[str] = None
    icon: Optional[str] = None
    tags: Optional[list[str]] = None
    examples: Optional[List[str]] = None
    deprecation_date: Optional[datetime] = None
    guard_types: Optional[List[str]] = None
    scanner_types: Optional[List[str]] = None
    modality_types: Optional[List[str]] = None
    created_at: datetime
    modified_at: datetime

    # Provider fields
    provider_id: UUID4
    provider_name: str
    provider_type: str
    provider_icon: str
    provider_description: str

    # Rules data
    items: List[RuleDetail]
