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

from typing import Any, Dict, Optional
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from budmicroframe.commons.schemas import ErrorResponse
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing_extensions import Annotated

from .schemas import (
    ModelArchitectureClassCreate,
    ModelArchitectureClassResponse,
    ModelArchitectureClassUpdate,
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
    supports_lora: Annotated[Optional[bool], Query(description="Filter by LoRA support")] = None,
    supports_pipeline_parallelism: Annotated[
        Optional[bool], Query(description="Filter by pipeline parallelism support")
    ] = None,
) -> ModelListResponse:
    """Get all models with optional search and pagination.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page
        search: Optional search term to filter by URI
        provider_id: Optional provider ID to filter by
        supports_lora: Optional filter for LoRA support
        supports_pipeline_parallelism: Optional filter for pipeline parallelism support

    Returns:
        List of models with pagination info
    """
    try:
        models, total = ModelService.get_all_models(
            page, page_size, search, provider_id, supports_lora, supports_pipeline_parallelism
        )
        return ModelListResponse(models=models, total=total, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


# Architecture endpoints - must be before /{model_id} to avoid route matching issues
@model_router.get("/architectures")
async def get_architectures(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in class name or family"),
) -> Dict[str, Any]:
    """Get all model architectures with pagination and search.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page
        search: Optional search term

    Returns:
        List of architectures with pagination info
    """
    try:
        architectures, total = ModelService.get_all_architectures(page, page_size, search)
        return {
            "architectures": architectures,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Error fetching architectures: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.get("/architectures/{architecture_id}", response_model=ModelArchitectureClassResponse)
async def get_architecture(architecture_id: UUID) -> ModelArchitectureClassResponse:
    """Get a specific architecture by ID.

    Args:
        architecture_id: UUID of the architecture

    Returns:
        Architecture details
    """
    try:
        architecture = ModelService.get_architecture_by_id(architecture_id)
        if not architecture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Architecture {architecture_id} not found",
            )
        return architecture
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching architecture {architecture_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.post("/architectures", response_model=ModelArchitectureClassResponse)
async def create_architecture(architecture_data: ModelArchitectureClassCreate) -> ModelArchitectureClassResponse:
    """Create a new model architecture.

    Args:
        architecture_data: Architecture creation data

    Returns:
        Created architecture
    """
    try:
        architecture = ModelService.create_architecture(architecture_data)
        return architecture
    except Exception as e:
        logger.error(f"Error creating architecture: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.patch("/architectures/{architecture_id}", response_model=ModelArchitectureClassResponse)
async def update_architecture(
    architecture_id: UUID, architecture_data: ModelArchitectureClassUpdate
) -> ModelArchitectureClassResponse:
    """Update an existing model architecture.

    Args:
        architecture_id: UUID of the architecture to update
        architecture_data: Architecture update data

    Returns:
        Updated architecture
    """
    try:
        architecture = ModelService.update_architecture(architecture_id, architecture_data)
        if not architecture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Architecture {architecture_id} not found",
            )
        return architecture
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating architecture {architecture_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.delete("/architectures/{architecture_id}")
async def delete_architecture(architecture_id: UUID) -> Dict[str, str]:
    """Delete a model architecture.

    Args:
        architecture_id: UUID of the architecture to delete

    Returns:
        Success message
    """
    try:
        success = ModelService.delete_architecture(architecture_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Architecture {architecture_id} not found",
            )
        return {"message": "Architecture deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting architecture {architecture_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@model_router.get("/{model_id}", response_model=ModelInfoResponse)
async def get_model(model_id: UUID) -> ModelInfoResponse:
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
async def create_model(model_data: ModelInfoCreate) -> ModelInfoResponse:
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
async def update_model(model_id: UUID, model_data: ModelInfoUpdate) -> ModelInfoResponse:
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
async def delete_model(model_id: UUID) -> None:
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
async def update_model_details(model_id: UUID, details_data: ModelDetailsUpdate) -> ModelDetailsResponse:
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
