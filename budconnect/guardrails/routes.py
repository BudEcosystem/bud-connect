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

"""API routes for guardrail operations."""

from typing import Literal, Optional

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from budmicroframe.commons.schemas import ErrorResponse
from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from pydantic import UUID4

from .services import GuardrailService


logger = logging.get_logger(__name__)


guardrail_router = APIRouter(prefix="/guardrail", tags=["Guardrail"])


@guardrail_router.get("/get-compatible-guardrails")
async def get_compatible_guardrails(
    engine: Literal["litellm", "tensorzero"],
    engine_version: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=0),
) -> JSONResponse:
    """Get the compatible guardrails for a given engine version."""
    # Calculate offset
    offset = (page - 1) * limit

    try:
        response = GuardrailService.get_compatible_probes(engine, offset, limit, engine_version)
        return response.to_http_response()
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        error_response = ErrorResponse(message=e.message, code=e.status_code)
        return error_response.to_http_response()
    except Exception as e:
        logger.exception(f"Error fetching compatible guardrails: {e}")
        error_response = ErrorResponse(
            message="Error fetching compatible guardrails:", code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return error_response.to_http_response()


@guardrail_router.get("/probes/{probe_id:path}/rules")
async def get_guardrail_details(
    probe_id: UUID4, page: int = Query(1, ge=1), limit: int = Query(5, ge=0)
) -> JSONResponse:
    """Get rules information for a specific probe by ID.

    Args:
        probe_id: The ID of the probe to get rules for.

    Returns:
        JSONResponse containing the probe rulesz or error message.
    """
    # Calculate offset
    offset = (page - 1) * limit

    try:
        response = GuardrailService.get_probe_rules(probe_id, offset, limit)
        if response:
            return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump(mode="json"))
        else:
            error_response = ErrorResponse(
                message=f"Rule details not found for probe ID: {probe_id}", code=status.HTTP_404_NOT_FOUND
            )
            return error_response.to_http_response()
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        error_response = ErrorResponse(message=e.message, code=e.status_code)
        return error_response.to_http_response()
    except Exception as e:
        logger.exception(f"Error fetching rule details: {e}")
        error_response = ErrorResponse(
            message="Error fetching rule details", code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return error_response.to_http_response()
