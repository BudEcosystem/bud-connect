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

"""License seeder to populate license data from a consolidated source."""

import json
import os
from typing import Any, Dict
from uuid import UUID

from budmicroframe.commons import logging

from ..commons.exceptions import SeederException
from ..model.crud import LicenseCRUD
from ..model.schemas import LicenseCreate
from .base import BaseSeeder


logger = logging.get_logger(__name__)

# Pre-defined paths
SEEDER_DIR = os.path.dirname(os.path.abspath(__file__))
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
        logger.error("File not found at %s", file_path)
        raise FileNotFoundError(f"File not found at {file_path}")

    with open(file_path, "r") as f:
        data: Dict[str, Any] = json.load(f)
        return data


class LicenseSeeder(BaseSeeder):
    """Seeder for populating license data from a consolidated file.

    This seeder loads licenses from a single JSON file that combines:
    - Licenses from the bud-runtime repository (86 licenses)
    - Custom licenses for proprietary APIs (OpenAI, etc.)
    - Provider-to-license mappings
    - Model-specific license overrides
    """

    def convert_license_format(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert license data to our schema format.

        Args:
            license_data: License data in either format

        Returns:
            Converted license data matching our schema
        """
        # Handle bud-runtime format
        if "license_id" in license_data:
            return {
                "key": license_data.get("license_id", ""),
                "name": license_data.get("license_name", ""),
                "type": license_data.get("type", "Unknown"),
                "type_description": license_data.get("description", ""),
                "type_suitability": license_data.get("suitability", "UNKNOWN"),
                "faqs": license_data.get("faqs", []),
            }
        # Already in our format
        else:
            return license_data

    async def load_licenses(self) -> Dict[str, Dict[str, Any]]:
        """Load all license definitions from the consolidated file.

        Returns:
            Dictionary mapping license keys to license data
        """
        try:
            data = read_json_file(LICENSES_PATH)

            # Handle both formats: list of licenses or dict with licenses key
            raw_licenses = data["licenses"] if isinstance(data, dict) and "licenses" in data else data

            # Convert to dictionary format
            licenses = {}
            for lic in raw_licenses:
                if not isinstance(lic, dict):
                    continue
                converted = self.convert_license_format(lic)
                key = converted.get("key")
                if key:
                    licenses[key] = converted

            logger.info("Loaded %d licenses from file", len(licenses))
            return licenses

        except FileNotFoundError:
            logger.error("Licenses file not found at %s", LICENSES_PATH)
            raise SeederException(f"Licenses file not found at {LICENSES_PATH}") from None
        except json.JSONDecodeError as e:
            logger.error("Failed to parse licenses file: %s", e)
            raise SeederException(f"Failed to parse licenses file: {e}") from e

    async def seed_licenses(self, licenses: Dict[str, Dict[str, Any]]) -> Dict[str, UUID]:
        """Seed license records to the database.

        Args:
            licenses: Dictionary mapping license keys to license data

        Returns:
            Dictionary mapping license keys to their database IDs
        """
        license_id_map = {}

        # Prepare all valid licenses for batch processing
        valid_licenses = []
        for license_key, license_info in licenses.items():
            # Validate required fields
            if not license_key or not license_info.get("name"):
                logger.warning("Skipping invalid license: %s", license_key)
                continue

            license_create = LicenseCreate(
                key=license_key,
                name=license_info["name"],
                type=license_info.get("type") or "Unknown",
                type_description=license_info.get("type_description") or "",
                type_suitability=license_info.get("type_suitability") or "UNKNOWN",
                faqs=license_info.get("faqs", []),
            )
            valid_licenses.append((license_key, license_create))

        # Process in batches to improve performance
        batch_size = 10
        with LicenseCRUD() as license_crud:
            for i in range(0, len(valid_licenses), batch_size):
                batch = valid_licenses[i : i + batch_size]
                logger.info(f"Processing license batch {i//batch_size + 1}/{(len(valid_licenses)-1)//batch_size + 1}")

                for license_key, license_create in batch:
                    try:
                        license_id = license_crud.upsert(data=license_create.model_dump(), conflict_target=["key"])
                        license_id_map[license_key] = license_id
                        logger.debug("Upserted license: %s -> %s", license_key, license_id)
                    except Exception as e:
                        logger.error("Failed to seed license %s: %s", license_key, e)
                        continue

        logger.info("Successfully seeded %d licenses", len(license_id_map))
        return license_id_map

    async def seed(self) -> None:
        """Load and seed all licenses.

        This method:
        1. Loads all licenses from the consolidated JSON file
        2. Seeds them to the database

        Raises:
            SeederException: If there is a critical error during seeding
        """
        try:
            # Load all licenses
            all_licenses = await self.load_licenses()

            if not all_licenses:
                logger.warning("No licenses found to seed")
                return

            # Seed to database
            license_id_map = await self.seed_licenses(all_licenses)

            logger.info("License seeding completed. Seeded %d licenses", len(license_id_map))

        except SeederException:
            raise
        except Exception as e:
            logger.exception("Unexpected error during license seeding: %s", e)
            raise SeederException("Failed to seed licenses") from e


if __name__ == "__main__":
    import asyncio

    asyncio.run(LicenseSeeder().seed())
