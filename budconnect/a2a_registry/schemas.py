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

"""Pydantic schemas for A2A registry agents."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import UUID4, BaseModel, ConfigDict


class A2ARegistryAgentCreate(BaseModel):
    """Schema for creating/upserting an A2A registry agent from the registry API."""

    registry_id: Optional[str] = None
    base_url: str
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    protocol_version: Optional[str] = None
    provider: Optional[Dict[str, Any]] = None
    skills: Optional[List[Dict[str, Any]]] = None
    capabilities: Optional[Dict[str, Any]] = None
    security_schemes: Optional[Dict[str, Any]] = None
    security: Optional[List[Dict[str, Any]]] = None
    icon_url: Optional[str] = None
    default_input_modes: Optional[List[str]] = None
    default_output_modes: Optional[List[str]] = None
    documentation_url: Optional[str] = None
    conformance: Optional[bool] = True
    is_healthy: Optional[bool] = None
    uptime_percentage: Optional[float] = None
    avg_response_time_ms: Optional[int] = None
    last_health_check: Optional[datetime] = None
    supports_authenticated_extended_card: Optional[bool] = None
    maintainer_notes: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: Optional[str] = None


class A2ARegistryAgentResponse(BaseModel):
    """Schema for A2A registry agent API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    registry_id: Optional[str] = None
    base_url: str
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    protocol_version: Optional[str] = None
    provider: Optional[Dict[str, Any]] = None
    skills: Optional[List[Dict[str, Any]]] = None
    capabilities: Optional[Dict[str, Any]] = None
    security_schemes: Optional[Dict[str, Any]] = None
    security: Optional[List[Dict[str, Any]]] = None
    icon_url: Optional[str] = None
    default_input_modes: Optional[List[str]] = None
    default_output_modes: Optional[List[str]] = None
    documentation_url: Optional[str] = None
    conformance: Optional[bool] = None
    is_healthy: Optional[bool] = None
    uptime_percentage: Optional[float] = None
    avg_response_time_ms: Optional[int] = None
    last_health_check: Optional[datetime] = None
    supports_authenticated_extended_card: Optional[bool] = None
    maintainer_notes: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: Optional[str] = None
    created_at: datetime
    modified_at: datetime


class A2ARegistryAgentListResponse(BaseModel):
    """Paginated list response for A2A registry agents."""

    agents: List[A2ARegistryAgentResponse] = []
    total: int = 0
    page: int = 1
    page_size: int = 50


class A2ARegistrySyncResponse(BaseModel):
    """Response schema for A2A registry sync operation."""

    status: str
    duration_seconds: float
    fetched: int = 0
    upserted: int = 0
    deleted: int = 0
