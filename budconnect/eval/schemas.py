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

"""Eval Pydantic schemas for API validation and serialization."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvalManifestBuildRequest(BaseModel):
    """Schema for triggering eval manifest build."""

    output_filename: str = Field(
        default="eval_manifest.json",
        description="Filename for the eval manifest (will be saved in budconnect/eval/data/)",
    )
    enable_analysis: bool = Field(
        default=False,
        description="Enable LLM-based analysis of dataset questions (samples 200 questions per dataset)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {"output_filename": "eval_manifest.json", "enable_analysis": False}
        }
    }


class EvalManifestBuildResponse(BaseModel):
    """Schema for eval manifest build response."""

    status: str = Field(
        description="Build status: 'success' (file created/updated), 'no_changes' (skipped), or 'failed'"
    )
    output_file: Optional[str] = None
    traits_count: Optional[int] = None
    datasets_count: Optional[int] = None
    last_updated: Optional[str] = None
    version: Optional[str] = Field(default=None, description="Manifest version (semantic versioning)")
    message: Optional[str] = Field(default=None, description="Human-readable status message")
    error: Optional[str] = None


class AvailableVersionsResponse(BaseModel):
    """Schema for listing available manifest versions."""

    latest_version: str = Field(description="Latest manifest version")
    available_versions: List[str] = Field(description="List of all available versions")
    total_count: int = Field(description="Total number of available versions")

    model_config = {
        "json_schema_extra": {
            "example": {
                "latest_version": "1.0.5",
                "available_versions": ["1.0.0", "1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.0.5"],
                "total_count": 6
            }
        }
    }
