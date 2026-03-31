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

"""API routes for A2A registry agent catalog."""

import asyncio
import time

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from budmicroframe.commons.schemas import ErrorResponse
from fastapi import APIRouter, HTTPException, Query, status

from .schemas import A2ARegistryAgentListResponse, A2ARegistrySyncResponse
from .services import A2ARegistryService


logger = logging.get_logger(__name__)

a2a_registry_router = APIRouter(prefix="/a2a-registry", tags=["A2A Registry"])

_a2a_registry_sync_lock = asyncio.Lock()


@a2a_registry_router.get("/agents", response_model=A2ARegistryAgentListResponse)
async def list_a2a_registry_agents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Number of items per page"),
) -> A2ARegistryAgentListResponse:
    """List A2A registry agents from local catalog.

    Serves paginated agents synced from a2aregistry.org for consumption by budapp.

    Args:
        page: Page number (1-indexed).
        page_size: Number of results per page.

    Returns:
        Paginated list of A2A registry agents.
    """
    try:
        result = A2ARegistryService.get_all_agents(page=page, page_size=page_size)
        return result
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        error_response = ErrorResponse(message=e.message, code=e.status_code)
        return error_response.to_http_response()
    except Exception as e:
        logger.exception(f"Error fetching A2A registry agents: {e}")
        error_response = ErrorResponse(
            message="Error fetching A2A registry agents", code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return error_response.to_http_response()


@a2a_registry_router.post("/cron-sync", response_model=A2ARegistrySyncResponse)
async def handle_a2a_registry_sync() -> A2ARegistrySyncResponse:
    """Dapr cron binding endpoint — triggers periodic A2A registry catalog sync.

    Protected by asyncio.Lock to prevent overlapping runs.
    """
    if _a2a_registry_sync_lock.locked():
        logger.warning("A2A registry sync already in progress, skipping this trigger")
        return A2ARegistrySyncResponse(status="skipped", duration_seconds=0.0)

    async with _a2a_registry_sync_lock:
        start_time = time.monotonic()
        logger.info("Starting periodic A2A registry catalog sync...")
        try:
            summary = await A2ARegistryService.sync()
            elapsed = time.monotonic() - start_time
            logger.info("A2A registry sync completed successfully in %.1f seconds", elapsed)
            return A2ARegistrySyncResponse(
                status="success",
                duration_seconds=round(elapsed, 1),
                **summary,
            )
        except Exception as e:
            elapsed = time.monotonic() - start_time
            logger.error("A2A registry sync failed after %.1f seconds: %s", elapsed, e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
