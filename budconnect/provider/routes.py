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

"""Routes for provider management."""

from typing import Optional
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from fastapi import APIRouter, HTTPException, Query, status

from .schemas import (
    ProviderCreate,
    ProviderListResponse,
    ProviderResponse,
    ProviderUpdate,
)
from .services import ProviderService


logger = logging.get_logger(__name__)

provider_router = APIRouter(prefix="/providers", tags=["Provider"])


@provider_router.get("/", response_model=ProviderListResponse)
async def get_providers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in provider name and type"),
) -> ProviderListResponse:
    """Get all providers with optional search and pagination.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page
        search: Optional search term to filter by name or type

    Returns:
        List of providers with pagination info
    """
    try:
        providers, total = ProviderService.get_all_providers(page, page_size, search)

        provider_responses = []
        for provider in providers:
            provider_responses.append(
                ProviderResponse(
                    id=provider["id"],
                    name=provider["name"],
                    provider_type=provider["provider_type"],
                    icon=provider["icon"],
                    description=provider["description"],
                    credentials=provider["credentials"],
                    model_count=provider.get("model_count", 0),
                    created_at=provider["created_at"],
                    modified_at=provider["modified_at"],
                )
            )

        return ProviderListResponse(providers=provider_responses, total=total, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error fetching providers: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@provider_router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: UUID) -> ProviderResponse:
    """Get a specific provider by ID.

    Args:
        provider_id: UUID of the provider

    Returns:
        Provider details
    """
    try:
        provider = ProviderService.get_provider_by_id(provider_id)
        return ProviderResponse(
            id=provider.id,
            name=provider.name,
            provider_type=provider.provider_type,
            icon=provider.icon,
            description=provider.description,
            credentials=provider.credentials,
            model_count=getattr(provider, "model_count", 0),
            created_at=provider.created_at,
            modified_at=provider.modified_at,
        )
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error fetching provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@provider_router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(provider_data: ProviderCreate) -> ProviderResponse:
    """Create a new provider.

    Args:
        provider_data: Provider creation data

    Returns:
        Created provider details
    """
    try:
        provider = ProviderService.create_provider(provider_data)
        return ProviderResponse(
            id=provider.id,
            name=provider.name,
            provider_type=provider.provider_type,
            icon=provider.icon,
            description=provider.description,
            credentials=provider.credentials,
            model_count=getattr(provider, "model_count", 0),
            created_at=provider.created_at,
            modified_at=provider.modified_at,
        )
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error creating provider: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@provider_router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(provider_id: UUID, provider_data: ProviderUpdate) -> ProviderResponse:
    """Update an existing provider.

    Args:
        provider_id: UUID of the provider to update
        provider_data: Update data (only provided fields will be updated)

    Returns:
        Updated provider details
    """
    try:
        provider = ProviderService.update_provider(provider_id, provider_data)
        return ProviderResponse(
            id=provider.id,
            name=provider.name,
            provider_type=provider.provider_type,
            icon=provider.icon,
            description=provider.description,
            credentials=provider.credentials,
            model_count=getattr(provider, "model_count", 0),
            created_at=provider.created_at,
            modified_at=provider.modified_at,
        )
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error updating provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@provider_router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider_id: UUID) -> None:
    """Delete a provider.

    Args:
        provider_id: UUID of the provider to delete

    Returns:
        No content on success
    """
    try:
        ProviderService.delete_provider(provider_id)
        return None
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error deleting provider {provider_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
