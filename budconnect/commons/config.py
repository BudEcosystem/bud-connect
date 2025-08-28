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

"""Manages application and secret configurations, utilizing environment variables and Dapr's configuration store for syncing."""

from pathlib import Path
from typing import Optional

from budmicroframe.commons.config import BaseAppConfig, BaseSecretsConfig, register_settings
from pydantic import DirectoryPath, Field

from ..__about__ import __version__


class AppConfig(BaseAppConfig):
    name: str = __version__.split("@")[0]
    version: str = __version__.split("@")[-1]
    description: str = ""
    api_root: str = ""

    # Base Directory
    base_dir: DirectoryPath = Path(__file__).parent.parent.parent.resolve()

    # LLM Configuration for License Extraction
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        alias="BUD_LLM_BASE_URL",
        description="Base URL for LLM API (OpenAI-compatible)",
    )
    llm_model: str = Field(default="gpt-4", alias="BUD_LLM_MODEL", description="LLM model name for license extraction")
    llm_api_key: Optional[str] = Field(
        default=None, alias="BUD_LLM_API_KEY", description="API key for LLM service (required for license extraction)"
    )
    llm_timeout: int = Field(default=120, alias="BUD_LLM_TIMEOUT", description="Timeout in seconds for LLM API calls")

    # Seeder Configuration
    run_seeders_on_startup: bool = Field(
        default=True,
        alias="RUN_SEEDERS_ON_STARTUP",
        description="Whether to run database seeders on application startup",
    )


class SecretsConfig(BaseSecretsConfig):
    name: str = __version__.split("@")[0]
    version: str = __version__.split("@")[-1]


app_settings = AppConfig()
secrets_settings = SecretsConfig()

register_settings(app_settings, secrets_settings)
