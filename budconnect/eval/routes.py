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

"""Eval API routes."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from .schemas import AvailableVersionsResponse, EvalManifestBuildRequest, EvalManifestBuildResponse
from .services import EvalService


eval_router = APIRouter(prefix="/eval", tags=["eval"])


@eval_router.get("/")
async def get_eval_status() -> Dict[str, Any]:
    """Get eval module status.

    Returns:
        dict: Status message and features
    """
    return {
        "status": "active",
        "message": "Eval manifest builder",
        "features": [
            "Fetches traits from OpenCompass API",
            "Fetches datasets from OpenCompass API",
            "Generates eval_manifest.json",
        ],
    }


@eval_router.post("/build", response_model=EvalManifestBuildResponse)
async def build_eval_manifest(request: EvalManifestBuildRequest) -> EvalManifestBuildResponse:
    """Build the eval manifest file.

    This endpoint will:
    1. Fetch traits data from OpenCompass API (listTopicDimensionTag)
    2. Fetch datasets data from OpenCompass API (listIndexCards)
    3. Transform and combine the data into eval_manifest.json format
    4. Optionally analyze datasets with LLM (if enable_analysis=True)
    5. Save to budconnect/eval/data/ directory

    Args:
        request: Build configuration with output filename and analysis options

    Returns:
        EvalManifestBuildResponse: Build result with status and details
    """
    service = EvalService()
    result = await service.build_manifest(
        output_filename=request.output_filename, enable_analysis=request.enable_analysis
    )

    return EvalManifestBuildResponse(**result)


@eval_router.get("/manifest", response_model=Dict[str, Any])
async def get_manifest(
    version: Optional[str] = Query(
        default=None,
        description="Manifest version (e.g., '1.0.5'). If not provided, returns latest version.",
        example="1.0.5"
    )
) -> Dict[str, Any]:
    """Get eval manifest by version.

    Returns the eval manifest JSON file. If version is specified, returns that specific version.
    If no version is provided, returns the latest version (follows symlink).

    Args:
        version: Optional version number (semantic versioning format: MAJOR.MINOR.PATCH)

    Returns:
        dict: Complete manifest JSON with traits and datasets

    Raises:
        404: Version not found or no manifest exists
        500: Failed to read or parse manifest file
    """
    service = EvalService()
    manifest_data = service.get_manifest(version=version)
    return manifest_data


@eval_router.get("/manifest/versions", response_model=AvailableVersionsResponse)
async def list_manifest_versions() -> AvailableVersionsResponse:
    """List all available manifest versions.

    Returns a list of all available manifest versions sorted in ascending order,
    along with the latest version identifier.

    Returns:
        AvailableVersionsResponse: Latest version, list of all versions, and total count
    """
    service = EvalService()
    result = service.list_available_versions()
    return AvailableVersionsResponse(**result)
