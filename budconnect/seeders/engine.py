import json
import logging
import os
from typing import Any, Dict, List

from ..engine.crud import (
    EngineCompatibilityCRUD,
    EngineCRUD,
    EngineToolParserRuleCRUD,
    EngineVersionCRUD,
)
from ..engine.schemas import (
    EngineCompatibilityCreate,
    EngineCreate,
    ParserMatchType,
)
from .base import BaseSeeder


logger = logging.getLogger(__name__)

# current file path
CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))

# seeder file path
ENGINE_SEEDER_FILE_PATH = os.path.join(CURRENT_FILE_PATH, "data", "engines.json")


class EngineSeeder(BaseSeeder):
    """Engine seeder."""

    async def seed(self) -> None:
        """Seed the database."""
        try:
            await self._seed_engine()
        except Exception as e:
            logger.exception(f"Failed to seed engine: {e}")

    @staticmethod
    async def _seed_engine() -> None:
        """Seed the engine."""
        engine_crud = EngineCRUD()
        engine_version_crud = EngineVersionCRUD()
        engine_compatibility_crud = EngineCompatibilityCRUD()
        engine_parser_rule_crud = EngineToolParserRuleCRUD()
        with engine_crud as engine_crud:
            existing_engines, _ = engine_crud.fetch_many()
        engines_data = EngineSeeder._get_engines_data()

        # Map engine seeder data by name for quick lookup
        engines_data_mapping = {engine["name"]: engine for engine in engines_data if "name" in engine}  # type: ignore
        # Process each engine in the JSON data
        for engine_name, engine_data in engines_data_mapping.items():
            # Check if engine already exists
            existing_engine = next((e for e in existing_engines if e.name == engine_name), None)

            if existing_engine:
                # Engine exists, use its ID
                engine_id = existing_engine.id
                logger.debug(f"Using existing engine: {engine_name} with ID {engine_id}")
            else:
                # Create new engine
                new_engine = EngineCreate(name=engine_name)
                with engine_crud as engine_crud:
                    created_engine = engine_crud.insert(new_engine.model_dump(exclude_unset=True))
                    engine_id = created_engine.id
                logger.info(f"Created new engine: {engine_name} with ID {engine_id}")

            # Process versions for this engine
            if "versions" in engine_data:
                for version_data in engine_data["versions"]:  # type: ignore
                    # Check if version already exists
                    with engine_version_crud as engine_version_crud:
                        existing_versions, _ = engine_version_crud.fetch_many(
                            {
                                "engine_id": engine_id,
                                "version": version_data["version"],  # type: ignore
                                "device_architecture": version_data["device_architecture"],  # type: ignore
                            }
                        )

                    if existing_versions:
                        # Version exists, use its ID
                        version_id = existing_versions[0].id
                    else:
                        # Create new version
                        new_version_data = {
                            "engine_id": str(engine_id),
                            "version": version_data["version"],  # type: ignore
                            "device_architecture": version_data["device_architecture"],  # type: ignore
                            "container_image": version_data["container_image"],  # type: ignore
                        }
                        with engine_version_crud as engine_version_crud:
                            created_version = engine_version_crud.insert(new_version_data)
                        version_id = created_version.id
                        logger.info(f"Created new version: {version_data['version']} with ID {version_id}")  # type: ignore

                    # Process compatibilities for this version
                    if "compatibilities" in version_data:
                        # Merge all architectures and features from all compatibilities
                        all_architectures: List[str] = []
                        all_features: List[str] = []

                        for compat_data in version_data["compatibilities"]:  # type: ignore
                            # Collect all architectures
                            all_architectures.extend(compat_data["architecture"])  # type: ignore

                            # Collect all features
                            all_features.extend(compat_data["features"])  # type: ignore

                        # Convert to dictionary format expected by the schema
                        architectures_dict = {"architectures": all_architectures}
                        features_dict = {"features": all_features}

                        # Determine supported tool calling templates and reasoning parsers based on engine
                        supported_tool_calling = []
                        supported_reasoning = []

                        # For vLLM engines, determine capabilities based on version
                        if engine_name.lower() == "vllm":
                            # vLLM supports various tool calling templates
                            supported_tool_calling = [
                                "hermes",
                                "mistral",
                                "llama3_json",
                                "internlm",
                                "jamba",
                                "xlam",
                                "qwen",
                                "minimax",
                                "deepseek",
                                "glm4",
                                "pythonic",
                            ]
                            # vLLM supports various reasoning parsers
                            supported_reasoning = [
                                "qwen3",
                                "mistral",
                                "glm4_moe",
                                "granite",
                                "step3",
                                "hunyuan_a13b",
                                "deepseek_r1",
                            ]

                        # Check if compatibility already exists for this version
                        existing_compat = engine_compatibility_crud.fetch_one({"engine_version_id": version_id})

                        if existing_compat:
                            # Update existing compatibility
                            update_data = {
                                "architectures": architectures_dict,
                                "features": features_dict,
                                "supported_tool_calling_parser_types": supported_tool_calling
                                if supported_tool_calling
                                else None,
                                "supported_reasoning_parsers": supported_reasoning if supported_reasoning else None,
                            }

                            # Update with the existing ID
                            engine_compatibility_crud.update(update_data, {"id": existing_compat.id})
                            logger.info(f"Updated compatibility for version {version_id}")
                        else:
                            # Create new compatibility
                            new_compat = EngineCompatibilityCreate(
                                engine_version_id=str(version_id),
                                architectures=architectures_dict,
                                features=features_dict,
                                supported_tool_calling_parser_types=supported_tool_calling
                                if supported_tool_calling
                                else None,
                                supported_reasoning_parsers=supported_reasoning if supported_reasoning else None,
                            )
                            engine_compatibility_crud.insert(new_compat.model_dump(exclude_unset=True))
                            logger.info(f"Created new compatibility for version {version_id}")

                    # Process tool parser rules for this version if provided
                    if "parser_rules" in version_data:
                        parser_rules = version_data.get("parser_rules", [])  # type: ignore
                        with engine_parser_rule_crud as parser_rule_crud:
                            parser_rule_crud.delete(
                                {"engine_version_id": version_id},
                                session=parser_rule_crud.session,
                                raise_on_error=False,
                            )

                            for rule in parser_rules:
                                parser_type = rule.get("parser_type")
                                if isinstance(parser_type, str):
                                    parser_type = parser_type.strip()
                                chat_template = rule.get("chat_template")
                                if isinstance(chat_template, str):
                                    chat_template = chat_template.strip()
                                rule_payload = {
                                    "engine_version_id": str(version_id),
                                    "parser_type": parser_type or None,
                                    "match_type": (rule.get("match_type") or "exact"),
                                    "pattern": rule.get("pattern"),
                                    "priority": rule.get("priority", 0),
                                    "enabled": rule.get("enabled", True),
                                    "notes": rule.get("notes"),
                                    "chat_template": chat_template or None,
                                }

                                match_type = rule_payload.get("match_type")
                                if isinstance(match_type, str):
                                    # Normalise to lowercase to match enum values
                                    normalized = match_type.lower()
                                    try:
                                        rule_payload["match_type"] = ParserMatchType(normalized).value
                                    except ValueError:
                                        logger.warning(
                                            "Skipping parser rule for engine version %s due to invalid match_type '%s'",
                                            version_id,
                                            match_type,
                                        )
                                        continue
                                elif isinstance(match_type, ParserMatchType):
                                    rule_payload["match_type"] = match_type.value

                                if (
                                    not rule_payload.get("parser_type") and not rule_payload.get("chat_template")
                                ) or not rule_payload.get("pattern"):
                                    logger.warning(
                                        "Skipping parser rule for engine version %s due to missing required fields",
                                        version_id,
                                    )
                                    continue

                                parser_rule_crud.insert(rule_payload, session=parser_rule_crud.session)
                                logger.info(
                                    "Added parser rule %s for engine version %s",
                                    rule_payload["parser_type"],
                                    version_id,
                                )

    @staticmethod
    def _get_engines_data() -> Dict[str, Any]:
        """Get engines data from the database."""
        try:
            with open(ENGINE_SEEDER_FILE_PATH, "r") as file:
                data: Dict[str, Any] = json.load(file)
                return data
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {ENGINE_SEEDER_FILE_PATH}") from e
