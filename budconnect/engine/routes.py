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

from typing import Union

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from budmicroframe.commons.schemas import ErrorResponse, SuccessResponse
from fastapi import APIRouter, status

from .schemas import DeviceArchitecture, LatestEngineVersionResponse
from .services import EngineService


logger = logging.get_logger(__name__)

engine_router = APIRouter(prefix="/engine", tags=["Engine"])


@engine_router.get("/check-model-compatibility")
async def check_model_compatibility(
    model_architecture: str, device_architecture: DeviceArchitecture, engine_version: str, engine: str
) -> Union[SuccessResponse, ErrorResponse]:
    """Check if a model architecture is compatible with a device architecture and engine version.

    Args:
        model_architecture: The architecture of the model to check compatibility for
        device_architecture: The architecture of the device (CUDA, ROCM, CPU, HPU)
        engine_version: The version of the engine to check compatibility against

    Returns:
        HTTP response with compatibility check results or error information
    """
    try:
        _ = EngineService.check_model_compatibility(model_architecture, device_architecture, engine_version, engine)
        response = SuccessResponse(
            message="Model architecture is compatible with the given device architecture and engine version",
            code=status.HTTP_200_OK,
            object="engine.compatibility",
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error checking model compatibility: {e}")
        response = ErrorResponse(message="Error checking model compatibility", code=500)

    return response.to_http_response()


@engine_router.get("/get-latest-engine-version")
async def get_latest_engine_version(
    device_architecture: DeviceArchitecture, engine: str
) -> Union[LatestEngineVersionResponse, ErrorResponse]:
    """Get the latest engine version for a device architecture."""
    try:
        latest_engine = EngineService.get_latest_engine_version(device_architecture, engine)

        response = LatestEngineVersionResponse(
            version=latest_engine.version,
            compatibilities=latest_engine.compatibilities,
            message="Engine version fetched successfully",
            code=status.HTTP_200_OK,
            object="engine.version",
        )
    except ClientException as e:
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error getting latest engine version: {e}")
        response = ErrorResponse(message="Error getting latest engine version", code=500)
    return response.to_http_response()
