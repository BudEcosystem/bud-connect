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

from typing import Any, Dict

from fastapi import APIRouter

from .schemas import EvalManifestBuildRequest, EvalManifestBuildResponse
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
