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

"""This module contains the routes for the model API."""

from typing import Literal, Optional
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from budmicroframe.commons.schemas import ErrorResponse
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing_extensions import Annotated

from .schemas import (
    ModelDetailsResponse,
    ModelDetailsUpdate,
    ModelInfoCreate,
    ModelInfoResponse,
    ModelInfoUpdate,
    ModelListResponse,
)
from .services import ModelService


logger = logging.get_logger(__name__)

model_router = APIRouter(prefix="/model", tags=["Model"])


@model_router.get("/get-compatible-models")
async def get_compatible_models(
    engine: Optional[str] = None,
    engine_version: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=0),
) -> JSONResponse:
    """Get compatible models for a given engine version, or all models if no engine specified."""
    # Calculate offset
    offset = (page - 1) * limit

    try:
        response = ModelService.get_compatible_models(engine, offset, limit, engine_version)
        return response.to_http_response()
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        error_response = ErrorResponse(message=e.message, code=e.status_code)
        return error_response.to_http_response()
    except Exception as e:
        logger.exception(f"Error fetching compatible models: {e}")
        error_response = ErrorResponse(
            message="Error fetching compatible models:", code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return error_response.to_http_response()


@model_router.get("/", response_model=ModelListResponse)
async def get_models(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in model URI"),
    provider_id: Annotated[Optional[UUID], Query(description="Filter by provider ID")] = None,
):
    """Get all models with optional search and pagination.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page
        search: Optional search term to filter by URI
        provider_id: Optional provider ID to filter by

    Returns:
        List of models with pagination info
    """
    try:
        models, total = ModelService.get_all_models(page, page_size, search, provider_id)
        return ModelListResponse(models=models, total=total, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.get("/{model_id}", response_model=ModelInfoResponse)
async def get_model(model_id: UUID):
    """Get a specific model by ID.

    Args:
        model_id: UUID of the model

    Returns:
        Model details
    """
    try:
        model = ModelService.get_model_by_id(model_id)
        return model
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error fetching model {model_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.post("/", response_model=ModelInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_model(model_data: ModelInfoCreate):
    """Create a new model.

    Args:
        model_data: Model creation data

    Returns:
        Created model details
    """
    try:
        model = ModelService.create_model(model_data)
        return model
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error creating model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.patch("/{model_id}", response_model=ModelInfoResponse)
async def update_model(model_id: UUID, model_data: ModelInfoUpdate):
    """Update an existing model.

    Args:
        model_id: UUID of the model to update
        model_data: Update data (only provided fields will be updated)

    Returns:
        Updated model details
    """
    try:
        model = ModelService.update_model(model_id, model_data)
        return model
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error updating model {model_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: UUID):
    """Delete a model.

    Args:
        model_id: UUID of the model to delete

    Returns:
        No content on success
    """
    try:
        ModelService.delete_model(model_id)
        return None
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error deleting model {model_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.get("/models/{model_uri:path}/details")
async def get_model_details(model_uri: str) -> JSONResponse:
    """Get detailed information for a specific model by URI.

    Args:
        model_uri: The URI of the model to get details for.

    Returns:
        JSONResponse containing the model details or error message.
    """
    try:
        response = ModelService.get_model_details(model_uri)
        if response:
            return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump(mode="json"))
        else:
            error_response = ErrorResponse(
                message=f"Model details not found for model URI: {model_uri}", code=status.HTTP_404_NOT_FOUND
            )
            return error_response.to_http_response()
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        error_response = ErrorResponse(message=e.message, code=e.status_code)
        return error_response.to_http_response()
    except Exception as e:
        logger.exception(f"Error fetching model details: {e}")
        error_response = ErrorResponse(
            message="Error fetching model details", code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return error_response.to_http_response()


@model_router.patch("/{model_id}/details", response_model=ModelDetailsResponse)
async def update_model_details(model_id: UUID, details_data: ModelDetailsUpdate):
    """Update model details including description, features, and pricing.

    Args:
        model_id: UUID of the model to update
        details_data: Details update data

    Returns:
        Updated model details
    """
    try:
        details = ModelService.update_model_details(model_id, details_data)
        return details
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except Exception as e:
        logger.error(f"Error updating model details {model_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
