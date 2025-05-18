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

from typing import Literal, Optional, Union

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from budmicroframe.commons.schemas import ErrorResponse
from fastapi import APIRouter, Query, status

from .schemas import CompatibleModelsResponse
from .services import ModelService


logger = logging.get_logger(__name__)

model_router = APIRouter(prefix="/model", tags=["Model"])


@model_router.get("/get-compatible-models")
async def get_compatible_models(
    engine: Literal["litellm"],
    engine_version: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=0),
) -> Union[CompatibleModelsResponse, ErrorResponse]:
    """Get the compatible models for a given engine version."""
    # Calculate offset
    offset = (page - 1) * limit

    try:
        response = ModelService.get_compatible_models(engine, offset, limit, engine_version)
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=e.status_code)
    except Exception as e:
        logger.exception(f"Error fetching compatible models: {e}")
        response = ErrorResponse(
            message="Error fetching compatible models:", code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response.to_http_response()
