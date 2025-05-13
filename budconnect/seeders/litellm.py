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
import logging
import os
from typing import Any, Dict

from ..commons.exceptions import SeederException
from .base import BaseSeeder


# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Pre-defined paths
SEEDER_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_CONFIG_PATH = os.path.join(SEEDER_DIR, "data", "engines.json")
LITELLM_DATA_DIR = os.path.join(SEEDER_DIR, "data", "litellm")


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

        return provider_model_map


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
            # Load engine configuration
            engines = read_json_file(str(ENGINE_CONFIG_PATH))
            logger.debug("Loaded configuration for %d engines", len(engines))

            # Find LiteLLM engine configuration
            litellm_engines = [engine for engine in engines if engine.get("name") == "litellm"]
            if not litellm_engines:
                logger.warning("No LiteLLM engine found")
                return

            litellm_engine = litellm_engines[0]
            litellm_versions = litellm_engine.get("versions", [])

            if not litellm_versions:
                logger.warning("No versions defined for LiteLLM engine")
                return

            # Process each version
            for version_config in litellm_versions:
                version = version_config.get("version")
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

                print(model_data)

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
