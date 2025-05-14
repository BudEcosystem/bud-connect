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

"""The LiteLLM seeder, containing essential data structures for the LiteLLM microservice."""

import json
import os
from typing import Any, Dict

from budmicroframe.commons import logging

from ..commons.exceptions import SeederException
from ..engine.crud import EngineCRUD
from ..model.crud import ProviderCRUD
from ..model.schemas import LiteLLMModelInfo, ProviderCreate
from .base import BaseSeeder


logger = logging.get_logger(__name__)

# Pre-defined paths
SEEDER_DIR = os.path.dirname(os.path.abspath(__file__))
LITELLM_DATA_DIR = os.path.join(SEEDER_DIR, "data", "litellm")
LITELLM_PROVIDERS_PATH = os.path.join(LITELLM_DATA_DIR, "litellm_providers.json")


def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read and parse JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the parsed JSON data

    Raises:
        FileNotFoundError: If the file is not found
    """
    if not os.path.exists(file_path):
        logger.error("file not found at %s", file_path)
        raise FileNotFoundError(f"file not found at {file_path}")

    with open(file_path, "r") as f:
        return json.load(f)


class LiteLLMParser:
    """Parser for LiteLLM model data.

    This class contains methods to parse and transform LiteLLM model data
    from the source format to a structure suitable for database insertion.
    """

    @staticmethod
    async def parse_model_data(source_path: str) -> Dict[str, Dict[str, Any]]:
        """Parse LiteLLM model data from a source file and organize by provider.

        Args:
            source_path: Path to the JSON file containing model data

        Returns:
            Dict mapping providers to their models with model details

        Raises:
            SeederException: If there is an error parsing the model data
        """
        # Load raw model data
        model_data = read_json_file(str(source_path))
        logger.debug("Loaded %d models from LiteLLM data file", len(model_data))

        # Get unique providers
        providers = {item["litellm_provider"] for item in model_data.values()}
        logger.debug("Found %d providers in LiteLLM data", len(providers))

        # Organize models by provider
        provider_model_map = {}
        for provider in providers:
            provider_models = {}
            for model_name, model_info in model_data.items():
                if model_info["litellm_provider"] == provider:
                    provider_models[model_name] = model_info

            provider_model_map[provider] = provider_models

        # Read providers data
        predefined_providers = read_json_file(LITELLM_PROVIDERS_PATH)

        # Validate any missing providers with predefined providers
        missing_providers = set(predefined_providers.keys()) - set(provider_model_map.keys())
        if missing_providers:
            logger.warning("Missing providers: %s", missing_providers)
            raise SeederException("New providers found in LiteLLM data")

        # Parse models to a common schema
        parsed_model_data = {}
        for provider, models in provider_model_map.items():
            for model_uri, model_details in models.items():
                if provider not in parsed_model_data:
                    parsed_model_data[provider] = []

                model_details.pop("litellm_provider", None)
                # TODO: need to setup a proper mode for each model
                mode = ["text_input", "text_output"]
                if mode is None:
                    raise SeederException("Unable to determine modality for model: %s", model_uri)

                parsed_model_data[provider].append(
                    LiteLLMModelInfo(uri=model_uri, config=model_details, modality=mode)
                )

        return parsed_model_data


class LiteLLMSeeder(BaseSeeder):
    """Seeder for LiteLLM model data.

    This class handles the process of loading LiteLLM model data from files
    and preparing it for database insertion.
    """

    @staticmethod
    async def get_version_file_path(version: str) -> str:
        """Generate a file path for the LiteLLM model data file for a specific version.

        Args:
            version: The version string (e.g., "0.1.0")

        Returns:
            Path to the LiteLLM model data file

        Raises:
            ValueError: If the version string is invalid
        """
        if not version or not isinstance(version, str):
            raise ValueError("Version must be a non-empty string")

        # Replace periods with underscores in version
        sanitized_version = version.replace(".", "_")

        if not sanitized_version:
            raise ValueError("Version string contains no valid characters after sanitization")

        return os.path.join(LITELLM_DATA_DIR, f"litellm_v_{sanitized_version}.json")

    @staticmethod
    async def parse_model_data_by_version(version: str, file_path: str) -> Dict[str, Any]:
        """Parse LiteLLM model data based on the version specification.

        Different versions may require different parsing logic.

        Args:
            version: The version string (e.g., "0.1.0")
            file_path: Path to the model data file

        Returns:
            Parsed model data organized by provider

        Raises:
            ValueError: If the version is not supported
            SeederException: If there is an error parsing the data
        """
        if version in ["0.1.0"]:
            return await LiteLLMParser.parse_model_data(file_path)
        else:
            raise ValueError(f"Unsupported LiteLLM version: {version}")

    async def seed(self) -> None:
        """Seed the database with LiteLLM model data.

        This method:
        1. Loads the engine configuration
        2. Identifies LiteLLM engine versions
        3. Processes each version's model data
        4. Prepares data for database insertion

        Raises:
            SeederException: If there is an error during the seeding process
        """
        try:
            # Load LiteLLM engine configuration from database
            engine_crud = EngineCRUD()
            with engine_crud as crud, crud.get_session() as session:
                db_engine = engine_crud.fetch_one(conditions={"name": "litellm"}, session=session)
                if not db_engine:
                    logger.warning("No LiteLLM engine found")
                    return

                if not db_engine.versions:
                    logger.warning("No versions defined for LiteLLM engine")
                    return

            # Process each version
            for version_config in db_engine.versions:
                version = version_config.version
                if not version:
                    logger.warning("Skipping invalid version configuration: missing version number")
                    continue

                logger.debug("Processing LiteLLM version: %s", version)

                # Get and validate data file path
                data_file_path = await self.get_version_file_path(version)
                if not os.path.exists(data_file_path):
                    raise SeederException(f"LiteLLM data file not found for version {version}: {data_file_path}")

                # Parse model data
                model_data = await self.parse_model_data_by_version(version, data_file_path)

                # Read providers data
                predefined_providers = read_json_file(LITELLM_PROVIDERS_PATH)

                # Prepare data for database insertion
                for provider, _models in model_data.items():
                    provider_data = ProviderCreate(
                        name=predefined_providers[provider]["name"],
                        provider_type=provider,
                        icon=predefined_providers[provider]["icon"],
                        description=predefined_providers[provider]["description"],
                    )
                    logger.debug("Provider data: %s", provider_data)

                    # Upsert provider
                    with ProviderCRUD() as provider_crud:
                        provider_crud.upsert(data=provider_data.model_dump(), conflict_target=["provider_type"])

        except FileNotFoundError as e:
            logger.exception("File not found during LiteLLM seeding: %s", e)
            raise SeederException("File not found during LiteLLM seeding") from e
        except json.JSONDecodeError as e:
            logger.exception("JSON decoding error during LiteLLM seeding: %s", e)
            raise SeederException("JSON decoding error during LiteLLM seeding") from e
        except ValueError as e:
            logger.exception("Value error during LiteLLM seeding: %s", e)
            raise SeederException("Value error during LiteLLM seeding") from e
        except Exception as e:
            logger.exception("Unexpected error during LiteLLM seeding: %s", e)
            raise SeederException("Unexpected error during LiteLLM seeding") from e


if __name__ == "__main__":
    import asyncio

    asyncio.run(LiteLLMSeeder().seed())


# python -m budconnect.seeders.litellm
