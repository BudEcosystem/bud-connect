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
from uuid import UUID

from budmicroframe.commons import logging

from ..commons.constants import ModalityEnum, ModelEndpointEnum
from ..commons.exceptions import SeederException
from ..engine.crud import EngineCRUD
from ..model.crud import LicenseCRUD, ModelInfoCRUD, ProviderCRUD
from ..model.schemas import (
    CacheCost,
    Features,
    InputCost,
    LiteLLMModelInfo,
    MediaLimits,
    ModelInfoCreate,
    OutputCost,
    ProviderCreate,
    RateLimits,
    SearchContextCost,
    Tokens,
)
from .base import BaseSeeder


logger = logging.get_logger(__name__)

# Pre-defined paths
SEEDER_DIR = os.path.dirname(os.path.abspath(__file__))
LITELLM_DATA_DIR = os.path.join(SEEDER_DIR, "data", "litellm")
LITELLM_PROVIDERS_PATH = os.path.join(LITELLM_DATA_DIR, "litellm_providers.json")
LICENSES_PATH = os.path.join(SEEDER_DIR, "data", "licenses.json")


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


def get_license_key_for_model(model_uri: str, provider_type: str) -> str | None:
    """Get license key for a model based on its URI and provider.

    Args:
        model_uri: The model URI
        provider_type: The provider type

    Returns:
        License key if found, None otherwise
    """
    # This function is now mainly a fallback - most license_id should come directly from model data
    # Return None if we don't have specific knowledge about the license
    return None


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
        missing_providers = set(provider_model_map.keys()) - set(predefined_providers.keys())
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

                parsed_model_data[provider].append(LiteLLMModelInfo(uri=model_uri, config=model_details))

        return parsed_model_data

    async def create_model_info(
        self, model_data: LiteLLMModelInfo, provider_id: UUID, provider_type: str, license_id: UUID | None
    ) -> ModelInfoCreate:
        """Create a model info from the model data.

        Args:
            model_data: The model data
        """
        # Define explicit mappings for each configuration field to its category
        CONFIG_FIELD_MAPPING = {
            "input_cost_per_audio_per_second": "input_cost",
            "input_cost_per_video_per_second_above_8s_interval": "input_cost",
            "input_cost_per_image": "input_cost",
            "input_cost_per_token_batch_requests": "input_cost",
            "input_cost_per_audio_per_second_above_128k_tokens": "input_cost",
            "input_cost_per_token_cache_hit": "input_cost",
            "input_cost_per_video_per_second_above_15s_interval": "input_cost",
            "input_cost_per_video_per_second": "input_cost",
            "input_cost_per_token_batches": "input_cost",
            "input_cost_per_pixel": "input_cost",
            "input_cost_per_token_above_200k_tokens": "input_cost",
            "input_cost_per_video_per_second_above_128k_tokens": "input_cost",
            "input_cost_per_character": "input_cost",
            "input_cost_per_image_above_128k_tokens": "input_cost",
            "input_cost_per_token_above_128k_tokens": "input_cost",
            "input_cost_per_query": "input_cost",
            "input_cost_per_audio_token": "input_cost",
            "input_cost_per_token": "input_cost",
            "input_cost_per_request": "input_cost",
            "input_cost_per_second": "input_cost",
            "input_cost_per_character_above_128k_tokens": "input_cost",
            "input_dbu_cost_per_token": "input_cost",
            # Output costs
            "output_cost_per_pixel": "output_cost",
            "output_cost_per_token": "output_cost",
            "output_cost_per_character": "output_cost",
            "output_dbu_cost_per_token": "output_cost",
            "output_cost_per_image": "output_cost",
            "output_cost_per_token_above_200k_tokens": "output_cost",
            "output_cost_per_character_above_128k_tokens": "output_cost",
            "output_cost_per_second": "output_cost",
            "output_cost_per_audio_token": "output_cost",
            "output_cost_per_token_batches": "output_cost",
            "output_cost_per_token_above_128k_tokens": "output_cost",
            "output_cost_per_reasoning_token": "output_cost",
            "output_db_cost_per_token": "output_cost",
            # Cache costs
            "cache_read_input_token_cost": "cache_cost",
            "cache_read_input_audio_token_cost": "cache_cost",
            "cache_creation_input_audio_token_cost": "cache_cost",
            "cache_creation_input_token_cost": "cache_cost",
            # Token limits
            "max_input_tokens": "tokens",
            "max_tokens_per_document_chunk": "tokens",
            "max_query_tokens": "tokens",
            "max_output_tokens": "tokens",
            "max_tokens": "tokens",
            "tool_use_system_prompt_tokens": "tokens",
            # Rate limits
            "rpm": "rate_limits",
            "tpm": "rate_limits",
            "rpd": "rate_limits",
            # Media limits
            "max_audio_per_prompt": "media_limits",
            "max_document_chunks_per_query": "media_limits",
            "max_audio_length_hours": "media_limits",
            "max_images_per_prompt": "media_limits",
            "max_videos_per_prompt": "media_limits",
            "max_pdf_size_mb": "media_limits",
            "max_video_length": "media_limits",
            # Features
            "supports_web_search": "features",
            "supports_response_schema": "features",
            "supports_reasoning": "features",
            "supports_system_messages": "features",
            "supports_tool_choice": "features",
            "supports_parallel_function_calling": "features",
            "supports_assistant_prefill": "features",
            "supports_function_calling": "features",
            "supports_native_streaming": "features",
            "supports_prompt_caching": "features",
            # Search context costs
            "search_context_cost_per_query": "search_context_cost",
        }

        # Initialize category dictionaries
        categorized_data = {
            "input_cost": {},
            "output_cost": {},
            "cache_cost": {},
            "search_context_cost": {},
            "tokens": {},
            "rate_limits": {},
            "media_limits": {},
            "features": {},
        }

        # Categorize the model data
        for field, value in model_data.config.items():
            category = CONFIG_FIELD_MAPPING.get(field)
            if category:
                categorized_data[category][field] = value

        # Determine the modality of the model
        if model_data.uri in [
            "fireworks-ai-4.1b-to-16b",
            "fireworks-ai-above-16b",
            "fireworks-ai-moe-up-to-56b",
            "fireworks-ai-56b-to-176b",
            "fireworks-ai-default",
            "fireworks-ai-up-to-4b",
            "fireworks-ai-embedding-up-to-150m",
            "fireworks-ai-embedding-150m-to-350m",
        ]:
            model_specs = await self.derive_predefined_model_specs(model_data)
        else:
            model_specs = await self.derive_model_specs(model_data)

        if categorized_data["search_context_cost"]:
            search_context_cost_per_query = SearchContextCost(
                **categorized_data["search_context_cost"]["search_context_cost_per_query"]
            )
        else:
            search_context_cost_per_query = None

        # Create a model info schema
        return ModelInfoCreate(
            uri=model_data.uri,
            modality=model_specs["modalities"],
            endpoints=model_specs["endpoints"],
            provider_id=provider_id,
            input_cost=InputCost(**categorized_data["input_cost"]) if categorized_data["input_cost"] else None,
            output_cost=OutputCost(**categorized_data["output_cost"]) if categorized_data["output_cost"] else None,
            cache_cost=CacheCost(**categorized_data["cache_cost"]) if categorized_data["cache_cost"] else None,
            search_context_cost_per_query=search_context_cost_per_query,
            tokens=Tokens(**categorized_data["tokens"]) if categorized_data["tokens"] else None,
            rate_limits=RateLimits(**categorized_data["rate_limits"]) if categorized_data["rate_limits"] else None,
            media_limits=MediaLimits(**categorized_data["media_limits"]) if categorized_data["media_limits"] else None,
            features=Features(**categorized_data["features"]) if categorized_data["features"] else None,
            deprecation_date=model_data.config.get("deprecation_date"),
            license_id=license_id,
        )

    @staticmethod
    async def derive_predefined_model_specs(model_data: LiteLLMModelInfo) -> Dict[str, Any]:
        """Determine the modality adn endpoints of the predefined model.

        Args:
            model_data: The model data

        Returns:
            The modality and endpoints of the model
        """
        uri = model_data.uri

        if uri in [
            "fireworks-ai-4.1b-to-16b",
            "fireworks-ai-above-16b",
            "fireworks-ai-moe-up-to-56b",
            "fireworks-ai-56b-to-176b",
            "fireworks-ai-default",
            "fireworks-ai-up-to-4b",
        ]:
            return {
                "modalities": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
                "endpoints": [ModelEndpointEnum.COMPLETION, ModelEndpointEnum.CHAT],
            }
        elif uri in [
            "fireworks-ai-embedding-up-to-150m",
            "fireworks-ai-embedding-150m-to-350m",
        ]:
            return {
                "modalities": [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT],
                "endpoints": [ModelEndpointEnum.EMBEDDING],
            }

    @staticmethod
    async def derive_model_specs(model_data: LiteLLMModelInfo) -> Dict[str, Any]:
        """Determine the modality and endpoints of the model.

        Args:
            provider_data: The provider data
        """
        config = model_data.config

        # Initialize supported modalities
        supported_modalities = []
        supported_model_endpoints = []

        # Determine input modalities
        input_modalities = config.get("supported_modalities", [])
        for modality in input_modalities:
            if modality == "text":
                supported_modalities.append(ModalityEnum.TEXT_INPUT)
                supported_model_endpoints.extend([ModelEndpointEnum.COMPLETION, ModelEndpointEnum.CHAT])
            elif modality == "image":
                supported_modalities.append(ModalityEnum.IMAGE_INPUT)
                supported_model_endpoints.extend([ModelEndpointEnum.IMAGE_GENERATION])
            elif modality == "audio":
                supported_modalities.append(ModalityEnum.AUDIO_INPUT)
                supported_model_endpoints.extend(
                    [ModelEndpointEnum.AUDIO_TRANSCRIPTION, ModelEndpointEnum.AUDIO_SPEECH]
                )

        # Determine output modalities
        output_modalities = config.get("supported_output_modalities", [])
        for modality in output_modalities:
            if modality == "text":
                supported_modalities.append(ModalityEnum.TEXT_OUTPUT)
                supported_model_endpoints.extend([ModelEndpointEnum.COMPLETION, ModelEndpointEnum.CHAT])
            elif modality == "image":
                supported_modalities.append(ModalityEnum.IMAGE_OUTPUT)
                supported_model_endpoints.extend([ModelEndpointEnum.IMAGE_GENERATION])
            elif modality == "audio":
                supported_modalities.append(ModalityEnum.AUDIO_OUTPUT)
                supported_model_endpoints.extend([ModelEndpointEnum.AUDIO_SPEECH])
            elif modality == "code":
                supported_modalities.append(ModalityEnum.TEXT_OUTPUT)
                supported_model_endpoints.extend([ModelEndpointEnum.COMPLETION, ModelEndpointEnum.CHAT])

        # supports_embedding_image_input
        if config.get("supports_embedding_image_input", False):
            supported_modalities.append(ModalityEnum.IMAGE_INPUT)
            supported_model_endpoints.extend([ModelEndpointEnum.EMBEDDING])

        # supports_audio_input
        if config.get("supports_audio_input", False):
            supported_modalities.append(ModalityEnum.AUDIO_INPUT)
            supported_model_endpoints.extend([ModelEndpointEnum.AUDIO_TRANSCRIPTION])

        # supports_pdf_input
        if config.get("supports_pdf_input", False):
            # TODO: Enable when budserve supports file input
            pass

        # supports_video_input
        if config.get("supports_video_input", False):
            # TODO: Enable when budserve supports file input
            pass

        # supports_vision
        if config.get("supports_vision", False):
            supported_modalities.append(ModalityEnum.TEXT_INPUT)
            supported_modalities.append(ModalityEnum.IMAGE_INPUT)
            supported_modalities.append(ModalityEnum.IMAGE_OUTPUT)
            supported_model_endpoints.extend([ModelEndpointEnum.IMAGE_GENERATION, ModelEndpointEnum.CHAT])

        # supports_image_input
        if config.get("supports_image_input", False):
            supported_modalities.append(ModalityEnum.IMAGE_INPUT)
            supported_model_endpoints.extend([ModelEndpointEnum.IMAGE_GENERATION])

        # supports_audio_output
        if config.get("supports_audio_output", False):
            supported_modalities.append(ModalityEnum.AUDIO_OUTPUT)
            supported_model_endpoints.extend([ModelEndpointEnum.AUDIO_SPEECH])

        # Remove duplicates
        supported_modalities = list(set(supported_modalities))

        if not supported_modalities:
            # Get modalities from mode
            mode = config.get("mode")
            if mode == "chat":
                supported_modalities = [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.CHAT])
            elif mode == "embedding":
                supported_modalities = [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.EMBEDDING])
            elif mode == "completion":
                supported_modalities = [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.COMPLETION])
            elif mode == "image_generation":
                supported_modalities = [ModalityEnum.TEXT_INPUT, ModalityEnum.IMAGE_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.IMAGE_GENERATION])
            elif mode == "audio_transcription":
                supported_modalities = [ModalityEnum.AUDIO_INPUT, ModalityEnum.TEXT_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.AUDIO_TRANSCRIPTION])
            elif mode == "audio_speech":
                supported_modalities = [ModalityEnum.TEXT_INPUT, ModalityEnum.AUDIO_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.AUDIO_SPEECH])
            elif mode == "moderation":
                supported_modalities = [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.MODERATION])
            elif mode == "rerank":
                supported_modalities = [ModalityEnum.TEXT_INPUT, ModalityEnum.TEXT_OUTPUT]
                supported_model_endpoints.extend([ModelEndpointEnum.RERANK])

        # Get supported endpoints
        if config.get("supported_endpoints", []):
            # Get supported endpoints from config
            logger.debug("Found supported endpoints in config")
            supported_model_endpoints = []
            for endpoint in config.get("supported_endpoints", []):
                supported_model_endpoints.append(ModelEndpointEnum(endpoint))

        return {
            "modalities": list(set(supported_modalities)),
            "endpoints": list(set(supported_model_endpoints)),
        }


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
    async def get_parser_by_version(version: str) -> LiteLLMParser:
        """Get the parser for the LiteLLM model data based on the version specification.

        Different versions may require different parsing logic.

        Args:
            version: The version string (e.g., "0.1.0")
            file_path: Path to the model data file

        Returns:
            A parser for the LiteLLM model data

        Raises:
            ValueError: If the version is not supported
            SeederException: If there is an error parsing the data
        """
        if version in ["0.1.0"]:
            return LiteLLMParser()
        else:
            raise ValueError(f"Unsupported LiteLLM version: {version}")

    async def get_license_id_map(self) -> Dict[str, UUID]:
        """Get mapping of license keys to IDs from the database.

        Returns:
            Dict mapping license keys to their database IDs
        """
        license_id_map = {}

        with LicenseCRUD() as license_crud:
            session = license_crud.get_session()
            try:
                # Fetch all licenses from database using direct query
                from ..model.models import License

                licenses = session.query(License).all()
                for license in licenses:
                    license_id_map[license.key] = license.id
                logger.debug("Loaded %d licenses from database", len(license_id_map))
            except Exception as e:
                logger.warning("Failed to load licenses from database: %s", e)
                logger.info("Continuing with empty license mapping - models will have null license_id")

        return license_id_map

    async def seed(self) -> None:
        """Seed the database with LiteLLM model data.

        This method:
        1. Seeds license records
        2. Loads the engine configuration
        3. Identifies LiteLLM engine versions
        4. Processes each version's model data
        5. Prepares data for database insertion

        Raises:
            SeederException: If there is an error during the seeding process
        """
        try:
            # Get license ID mapping from database (assumes LicenseSeeder has already run)
            license_id_map = await self.get_license_id_map()
            if not license_id_map:
                logger.warning("No licenses found in database. Run LicenseSeeder first.")
                # Continue anyway - models will have null license_id
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
                litellm_parser = await self.get_parser_by_version(version)
                model_data = await litellm_parser.parse_model_data(data_file_path)

                # Read providers data
                predefined_providers = read_json_file(LITELLM_PROVIDERS_PATH)
                logger.debug("Predefined providers: %s", len(predefined_providers))

                if version == "0.1.0":
                    # NOTE: Upsert huggingface default provider
                    hf_provider_type = "huggingface"
                    hf_provider_data = ProviderCreate(
                        name=predefined_providers[hf_provider_type]["name"],
                        provider_type=hf_provider_type,
                        icon=predefined_providers[hf_provider_type]["icon"],
                        description=predefined_providers[hf_provider_type]["description"],
                        credentials=predefined_providers[hf_provider_type]["credentials"],
                    )

                    # Upsert provider
                    with ProviderCRUD() as hf_provider_crud:
                        db_provider_id = hf_provider_crud.upsert(
                            data=hf_provider_data.model_dump(), conflict_target=["provider_type"]
                        )
                        logger.debug("Upserted provider: %s", db_provider_id)
                        hf_provider_crud.add_engine_version(db_provider_id, version_config.id)

                # Prepare data for database insertion
                for provider, supported_models in model_data.items():
                    provider_data = ProviderCreate(
                        name=predefined_providers[provider]["name"],
                        provider_type=provider,
                        icon=predefined_providers[provider]["icon"],
                        description=predefined_providers[provider]["description"],
                        credentials=predefined_providers[provider]["credentials"],
                    )

                    # Upsert provider
                    with ProviderCRUD() as provider_crud:
                        db_provider_id = provider_crud.upsert(
                            data=provider_data.model_dump(), conflict_target=["provider_type"]
                        )
                        logger.debug("Upserted provider: %s", db_provider_id)
                        provider_crud.add_engine_version(db_provider_id, version_config.id)

                    # Parse model info
                    for model in supported_models:
                        # Get license ID from model data directly, or fall back to mapping
                        license_key = model.config.get("license_id")
                        if not license_key:
                            license_key = get_license_key_for_model(model.uri, provider)
                        license_id = license_id_map.get(license_key) if license_key else None

                        model_info_data = await litellm_parser.create_model_info(
                            model, db_provider_id, provider, license_id
                        )

                        # Upsert model info
                        with ModelInfoCRUD() as model_info_crud:
                            db_model_info_id = model_info_crud.upsert(
                                data=model_info_data.model_dump(),
                                conflict_target=["uri"],
                            )
                            logger.debug("Upserted model info: %s", db_model_info_id)
                            model_info_crud.add_engine_version(db_model_info_id, version_config.id)

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
