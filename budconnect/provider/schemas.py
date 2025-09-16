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

"""Schemas for provider module."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CredentialField(BaseModel):
    """Schema for a credential field definition."""

    field: str = Field(..., description="Field name for the credential")
    label: str = Field(..., description="Display label for the field")
    type: str = Field(..., description="Field type (password, text, select, etc.)")
    description: str = Field(..., description="Help text for the field")
    required: bool = Field(..., description="Whether this field is required")
    order: int = Field(..., description="Display order of the field")
    options: Optional[List[str]] = Field(None, description="Options for select fields")
    default: Optional[str] = Field(None, description="Default value for the field")


class ProviderCreate(BaseModel):
    """Schema for creating a provider."""

    name: str = Field(..., description="Display name of the provider")
    provider_type: str = Field(..., description="Unique identifier type for the provider")
    icon: str = Field(..., description="Path or URL to the provider's icon")
    description: str = Field(..., description="Description of the provider")
    credentials: List[CredentialField] = Field(
        default_factory=list, description="List of credential fields required for this provider"
    )


class ProviderUpdate(BaseModel):
    """Schema for updating a provider."""

    name: Optional[str] = Field(None, description="Display name of the provider")
    icon: Optional[str] = Field(None, description="Path or URL to the provider's icon")
    description: Optional[str] = Field(None, description="Description of the provider")
    credentials: Optional[List[CredentialField]] = Field(
        None, description="List of credential fields required for this provider"
    )


class ProviderResponse(BaseModel):
    """Schema for provider response."""

    id: UUID
    name: str
    provider_type: str
    icon: str
    description: str
    credentials: List[CredentialField]
    model_count: int = Field(0, description="Number of models associated with this provider")
    created_at: datetime
    modified_at: datetime

    class Config:
        """Configuration for the ProviderResponse model."""

        from_attributes = True


class ProviderListResponse(BaseModel):
    """Schema for paginated provider list response."""

    providers: List[ProviderResponse]
    total: int
    page: int
    page_size: int
