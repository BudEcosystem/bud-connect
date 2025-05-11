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
from budmicroframe.commons.schemas import ErrorResponse
from fastapi import APIRouter, status

from .schemas import CompatibleEnginesResponse, DeviceArchitecture, LatestEngineVersionResponse
from .services import EngineService


logger = logging.get_logger(__name__)

engine_router = APIRouter(prefix="/engine", tags=["Engine"])


@engine_router.get("/get-compatible-engines")
async def get_compatible_engines(
    model_architecture: str,
    device_architecture: Union[DeviceArchitecture, None] = None,
    engine_version: Union[str, None] = None,
    engine: Union[str, None] = None,
) -> Union[CompatibleEnginesResponse, ErrorResponse]:
    """Check if a model architecture is compatible with a device architecture and engine version.

    Args:
        model_architecture: The architecture of the model to check compatibility for
        device_architecture: The architecture of the device (CUDA, ROCM, CPU, HPU)
        engine_version: The version of the engine to check compatibility against

    Returns:
        HTTP response with compatibility check results or error information
    """
    try:
        # Cast Optional types to their required types as expected by the service
        compatible_engines = EngineService.get_compatible_engines(
            model_architecture=model_architecture,
            device_architecture=device_architecture,  # type: ignore
            engine_version=engine_version,  # type: ignore
            engine=engine,  # type: ignore
        )
        response = CompatibleEnginesResponse(
            message="Model architecture is compatible with the given device architecture and engine version",
            code=status.HTTP_200_OK,
            object="engine.compatibility",
            compatible_engines=compatible_engines,
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
