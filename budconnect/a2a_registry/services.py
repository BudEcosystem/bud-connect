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

"""Service layer for A2A registry agent sync and retrieval."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from budmicroframe.commons import logging

from .crud import A2ARegistryAgentCRUD
from .schemas import A2ARegistryAgentCreate, A2ARegistryAgentListResponse, A2ARegistryAgentResponse


logger = logging.get_logger(__name__)

A2A_REGISTRY_URL = "https://a2aregistry.org/api/agents"
FETCH_LIMIT = 50
FETCH_TIMEOUT_SECONDS = 30
MAX_PAGES = 50  # Safety cap: 50 pages × 50 = 2500 agents max
CIRCUIT_BREAKER_THRESHOLD = 3
CIRCUIT_BREAKER_COOLDOWN_SECONDS = 3600  # 1 hour


class A2ARegistryService:
    """Service for fetching A2A agents from a2aregistry.org and managing local storage."""

    # Circuit breaker state (module-level, shared across instances)
    _consecutive_failures: int = 0
    _circuit_open_until: Optional[datetime] = None

    @staticmethod
    def _map_registry_agent(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Map a camelCase registry agent to snake_case DB fields.

        Args:
            raw: Raw agent dict from registry API response.

        Returns:
            Dict with snake_case keys matching A2ARegistryAgentCreate fields.
        """
        return {
            "registry_id": str(raw.get("id", "")),
            "base_url": raw.get("url", ""),
            "name": raw.get("name", ""),
            "description": raw.get("description"),
            "author": raw.get("author"),
            "version": raw.get("version"),
            "protocol_version": raw.get("protocolVersion"),
            "provider": raw.get("provider"),
            "skills": raw.get("skills"),
            "capabilities": raw.get("capabilities"),
            "security_schemes": raw.get("securitySchemes"),
            "security": raw.get("security"),
            "icon_url": raw.get("iconUrl"),
            "default_input_modes": raw.get("defaultInputModes"),
            "default_output_modes": raw.get("defaultOutputModes"),
            "documentation_url": raw.get("documentationUrl"),
            "conformance": raw.get("conformance"),
            "is_healthy": raw.get("is_healthy"),
            "uptime_percentage": raw.get("uptime_percentage"),
            "avg_response_time_ms": raw.get("avg_response_time_ms"),
            "last_health_check": raw.get("last_health_check"),
            "supports_authenticated_extended_card": raw.get("supportsAuthenticatedExtendedCard"),
            "maintainer_notes": raw.get("maintainer_notes"),
            "homepage": raw.get("homepage"),
            "repository": raw.get("repository"),
            "license": raw.get("license"),
        }

    @classmethod
    def _is_circuit_open(cls) -> bool:
        """Check if circuit breaker is open (should skip fetching)."""
        if cls._circuit_open_until is None:
            return False
        if datetime.now(timezone.utc) >= cls._circuit_open_until:
            cls._circuit_open_until = None
            cls._consecutive_failures = 0
            logger.info("A2A registry circuit breaker reset")
            return False
        return True

    @classmethod
    def _record_failure(cls) -> None:
        """Record a fetch failure and potentially open circuit breaker."""
        cls._consecutive_failures += 1
        if cls._consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            from datetime import timedelta

            cls._circuit_open_until = datetime.now(timezone.utc) + timedelta(seconds=CIRCUIT_BREAKER_COOLDOWN_SECONDS)
            logger.warning(
                "A2A registry circuit breaker OPEN after %d failures, cooling down for %ds",
                cls._consecutive_failures,
                CIRCUIT_BREAKER_COOLDOWN_SECONDS,
            )

    @classmethod
    def _record_success(cls) -> None:
        """Record a successful fetch and reset circuit breaker."""
        cls._consecutive_failures = 0
        cls._circuit_open_until = None

    @classmethod
    async def fetch_from_registry(cls) -> List[Dict[str, Any]]:
        """Fetch standard, healthy A2A agents from a2aregistry.org.

        Paginates with limit=50 + offset. Stops when len(agents) < limit.
        Applies circuit breaker: skips after 3 consecutive failures for 1 hour.

        Returns:
            List of snake_case agent dicts ready for A2ARegistryAgentCreate.
        """
        if cls._is_circuit_open():
            logger.warning("A2A registry circuit breaker is open, skipping fetch")
            return []

        all_agents: List[Dict[str, Any]] = []
        timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT_SECONDS)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for page in range(MAX_PAGES):
                    offset = page * FETCH_LIMIT
                    params = {
                        "conformance": "standard",
                        "healthy": "true",
                        "limit": str(FETCH_LIMIT),
                        "offset": str(offset),
                    }
                    async with session.get(A2A_REGISTRY_URL, params=params) as resp:
                        if resp.status != 200:
                            cls._record_failure()
                            raise RuntimeError(f"A2A registry returned status {resp.status}")

                        data = await resp.json()
                        agents = data.get("agents", [])

                        for raw_agent in agents:
                            mapped = cls._map_registry_agent(raw_agent)
                            if mapped["base_url"]:
                                all_agents.append(mapped)

                        if len(agents) < FETCH_LIMIT:
                            break

            cls._record_success()
            logger.info("Fetched %d standard A2A agents from registry", len(all_agents))
            return all_agents

        except Exception as e:
            cls._record_failure()
            logger.error("Failed to fetch from A2A registry: %s", e)
            raise

    @staticmethod
    async def sync() -> Dict[str, int]:
        """Full sync workflow: fetch → upsert → delete absent → return summary.

        Returns:
            Dict with keys: fetched, upserted, deleted.
        """
        agents = await A2ARegistryService.fetch_from_registry()
        if not agents:
            logger.warning("No A2A agents fetched from registry, skipping sync")
            return {"fetched": 0, "upserted": 0, "deleted": 0}

        crud = A2ARegistryAgentCRUD()
        current_base_urls = set()
        upserted = 0

        with crud as crud_ctx:
            session = crud_ctx.get_session()
            for agent_data in agents:
                try:
                    create_schema = A2ARegistryAgentCreate(**agent_data)
                    crud.upsert_by_base_url(create_schema.model_dump(), session=session)
                    current_base_urls.add(agent_data["base_url"])
                    upserted += 1
                except Exception as e:
                    logger.warning("Failed to upsert agent %s: %s", agent_data.get("base_url", "?"), e)
            session.commit()

        deleted = 0
        if current_base_urls:
            with crud as crud_ctx:
                session = crud_ctx.get_session()
                deleted = crud.delete_absent(current_base_urls, session=session)
                session.commit()

        summary = {"fetched": len(agents), "upserted": upserted, "deleted": deleted}
        logger.info("A2A registry sync complete: %s", summary)
        return summary

    @staticmethod
    def get_all_agents(
        page: int = 1,
        page_size: int = 50,
    ) -> A2ARegistryAgentListResponse:
        """Get paginated A2A registry agents from local DB.

        Args:
            page: Page number (1-indexed).
            page_size: Results per page.

        Returns:
            A2ARegistryAgentListResponse with agents and pagination info.
        """
        crud = A2ARegistryAgentCRUD()
        with crud as crud_ctx:
            session = crud_ctx.get_session()
            total, agents = crud.fetch_many(page=page, page_size=page_size, session=session)

        agent_responses = [A2ARegistryAgentResponse.model_validate(agent) for agent in agents]

        return A2ARegistryAgentListResponse(
            agents=agent_responses,
            total=total,
            page=page,
            page_size=page_size,
        )
