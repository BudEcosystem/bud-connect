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

"""SQLAlchemy model for A2A registry agents fetched from a2aregistry.org."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from budmicroframe.shared.psql_service import PSQLBase, TimestampMixin
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


class A2ARegistryAgent(PSQLBase, TimestampMixin):
    """A2A agent fetched from the public a2aregistry.org catalog.

    Stores standard, healthy A2A agents for discovery. Synced periodically
    from a2aregistry.org and served to budapp via paginated API.

    Attributes:
        id: Internal UUID primary key.
        registry_id: Original UUID from the a2aregistry.org API.
        base_url: Agent's base URL — unique dedup key. The well-known agent card
            URL is derived at runtime as {base_url}/.well-known/agent.json.
        name: Human-readable agent name.
        description: Agent description/purpose.
        author: Author or organization name from registry.
        version: Agent version string.
        protocol_version: A2A protocol version (e.g., "0.3.0").
        provider: Provider info as JSON object {organization, url}.
        skills: Array of skill objects [{id, name, description, tags, ...}].
        capabilities: Capability flags {streaming, pushNotifications, ...}.
        security_schemes: SecuritySchemes object (currently {} for most agents).
        security: Security requirements array (currently [] for most agents).
        icon_url: Agent icon URL.
        default_input_modes: Supported input MIME types.
        default_output_modes: Supported output MIME types.
        documentation_url: Link to agent documentation.
        conformance: True if agent conforms to A2A standard protocol.
        is_healthy: Health status from registry health checks.
        uptime_percentage: Uptime percentage from registry monitoring.
        avg_response_time_ms: Average response time in milliseconds.
        last_health_check: Timestamp of last registry health check.
        supports_authenticated_extended_card: Whether agent supports authenticated extended card.
        maintainer_notes: Registry maintainer notes about the agent.
        homepage: Agent homepage URL.
        repository: Source code repository URL.
        license: License type string.
    """

    __tablename__ = "a2a_registry_agent"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    registry_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    base_url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    protocol_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    provider: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    skills: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    capabilities: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    security_schemes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    security: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    icon_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    default_input_modes: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    default_output_modes: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    documentation_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    conformance: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)
    is_healthy: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    uptime_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    supports_authenticated_extended_card: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    maintainer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    homepage: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    repository: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    license: Mapped[Optional[str]] = mapped_column(String, nullable=True)
