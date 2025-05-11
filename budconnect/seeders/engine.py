import json
import logging
import os
from typing import Any, Dict

from ..engine.crud import EngineCompatibilityCRUD, EngineCRUD, EngineVersionCRUD
from ..engine.schemas import DeviceArchitecture, Engine, EngineCompatibility, EngineVersion
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
                new_engine = Engine(name=engine_name)
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
                                "device_architecture": DeviceArchitecture(version_data["device_architecture"]),  # type: ignore
                            }
                        )

                    if existing_versions:
                        # Version exists, use its ID
                        version_id = existing_versions[0].id
                    else:
                        # Create new version
                        new_version = EngineVersion(
                            engine_id=str(engine_id),
                            version=version_data["version"],  # type: ignore
                            device_architecture=version_data["device_architecture"],  # type: ignore
                            container_image=version_data["container_image"],  # type: ignore
                        )
                        with engine_version_crud as engine_version_crud:
                            created_version = engine_version_crud.insert(new_version.model_dump(exclude_unset=True))
                        version_id = created_version.id
                        logger.info(f"Created new version: {version_data['version']} with ID {version_id}")  # type: ignore

                    # Process compatibilities for this version
                    if "compatibilities" in version_data:
                        # Merge all architectures and features from all compatibilities
                        all_architectures = []
                        all_features = []

                        for compat_data in version_data["compatibilities"]:  # type: ignore
                            # Convert architecture strings to dictionaries
                            all_architectures.extend([{"name": arch} for arch in compat_data["architecture"]])  # type: ignore

                            # Convert feature strings to dictionaries
                            all_features.extend([{"name": feature} for feature in compat_data["features"]])  # type: ignore

                        # Check if compatibility already exists for this version
                        existing_compat = engine_compatibility_crud.fetch_one({"engine_version_id": version_id})

                        if existing_compat:
                            # Use dot notation to access object attributes
                            update_data = {
                                "engine_version_id": existing_compat.engine_version_id,
                                "architectures": existing_compat.architectures,
                                "features": existing_compat.features,
                                # Other fields as needed
                            }

                            # Update with the existing ID
                            engine_compatibility_crud.update(update_data, {"id": existing_compat.id})
                            logger.info(f"Updated compatibility for version {version_id}")
                        else:
                            # Create new compatibility
                            new_compat = EngineCompatibility(
                                engine_version_id=str(version_id),
                                architectures=all_architectures,
                                features=all_features,
                            )
                            engine_compatibility_crud.insert(new_compat.model_dump(exclude_unset=True))
                            logger.info(f"Created new compatibility for version {version_id}")

    @staticmethod
    def _get_engines_data() -> Dict[str, Any]:
        """Get engines data from the database."""
        try:
            with open(ENGINE_SEEDER_FILE_PATH, "r") as file:
                data: Dict[str, Any] = json.load(file)
                return data
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {ENGINE_SEEDER_FILE_PATH}") from e
