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

"""The Guardrails seeder, containing essential data structures for the Guardrails microservice."""

import json
import os
from typing import Any, Dict, List

from budmicroframe.commons import logging

from ..commons.exceptions import SeederException
from ..engine.crud import EngineCRUD
from ..guardrails.crud import GuardrailProbeCRUD, GuardrailRuleCRUD
from ..model.crud import ProviderCRUD
from .base import BaseSeeder


logger = logging.get_logger(__name__)

# Pre-defined paths
SEEDER_DIR = os.path.dirname(os.path.abspath(__file__))
GUARDRAILS_DATA_PATH = os.path.join(SEEDER_DIR, "data", "guardrails.json")


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Read and parse JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        List containing the parsed JSON data

    Raises:
        FileNotFoundError: If the file is not found
    """
    if not os.path.exists(file_path):
        logger.error("file not found at %s", file_path)
        raise FileNotFoundError(f"file not found at {file_path}")

    with open(file_path, "r") as f:
        data: List[Dict[str, Any]] = json.load(f)
        return data


class GuardrailsSeeder(BaseSeeder):
    """Seeder for Guardrails probe and rule data.

    This class handles the process of loading Guardrails data from files
    and preparing it for database insertion.
    """

    async def seed(self) -> None:
        """Seed the database with Guardrails probe and rule data.

        This method:
        1. Loads the guardrails data from JSON file
        2. Groups data by provider type
        3. Gets provider IDs from database
        4. Creates probes and rules in the database

        Raises:
            SeederException: If there is an error during the seeding process
        """
        try:
            # Initialize counters
            probe_upserts = 0
            rule_upserts = 0

            # Load guardrails data
            guardrails_data = read_json_file(GUARDRAILS_DATA_PATH)
            logger.info("Loaded %d provider guardrail sets from data file", len(guardrails_data))

            # Get engine configuration from database
            engine_crud = EngineCRUD()
            with engine_crud as crud, crud.get_session() as session:
                # Try both tensorzero and bud_sentinel engines
                db_engine = engine_crud.fetch_one(conditions={"name": "tensorzero"}, session=session)
                if db_engine:
                    logger.info("Found %s engine", "tensorzero")
                elif not db_engine:
                    logger.warning("No TensorZero engine found")
                    return

                if not db_engine.versions:
                    logger.warning("No versions defined for %s engine", db_engine.name)
                    return

                # Get the latest version
                # version_config = db_engine.versions[0]  # Assuming first version is the latest

            # Process each provider's guardrails
            for provider_guardrails in guardrails_data:
                provider_type = provider_guardrails["provider_type"]
                probes = provider_guardrails.get("probes", [])

                # Initialize per-provider counters
                provider_probe_upserts = 0
                provider_rule_upserts = 0

                logger.info("Processing %d probes for provider %s", len(probes), provider_type)

                # Get provider from database
                with ProviderCRUD() as provider_crud:
                    db_provider = provider_crud.fetch_one(conditions={"provider_type": provider_type})
                    if not db_provider:
                        logger.warning("Provider %s not found in database", provider_type)
                        continue

                    provider_id = db_provider.id

                # Process each probe
                for probe_data in probes:
                    probe_uri = probe_data["id"]  # For probes, URI is same as ID

                    # Create probe data
                    probe_create_data = {
                        "name": probe_data["title"],
                        "uri": probe_uri,
                        "description": probe_data.get("description"),
                        "tags": probe_data.get("tags", []),
                        "provider_id": provider_id,
                        "deprecation_date": probe_data.get("deprecation_date"),
                    }

                    # Upsert probe
                    with GuardrailProbeCRUD() as probe_crud:
                        db_probe_id = probe_crud.upsert(data=probe_create_data, conflict_target=["uri"])
                        probe_upserts += 1
                        provider_probe_upserts += 1

                    # Process rules for this probe
                    rules = probe_data.get("rules", [])
                    for rule_data in rules:
                        rule_id = rule_data["id"]
                        # Create rule URI based on the pattern: scanners[0]/rule_id
                        scanners = rule_data.get("scanners", [])
                        rule_uri = (
                            f"{scanners[0]}/{rule_id}" if scanners and provider_type == "bud_sentinel" else rule_id
                        )

                        # Create rule data
                        rule_create_data = {
                            "probe_id": db_probe_id,
                            "name": rule_data["title"],
                            "uri": rule_uri,
                            "description": rule_data.get("description"),
                            "examples": rule_data.get("examples", []),
                            "guard_types": rule_data.get("guard_types", []),
                            "scanner_types": rule_data.get("scanners", []),
                            "modality_types": rule_data.get("modalities", []),
                            "deprecation_date": rule_data.get("deprecation_date"),
                        }

                        # Upsert rule
                        with GuardrailRuleCRUD() as rule_crud:
                            rule_crud.upsert(data=rule_create_data, conflict_target=["uri"])
                            rule_upserts += 1
                            provider_rule_upserts += 1

                # Log summary for this provider
                logger.info(
                    "Completed seeding guardrails for provider %s - Probes upserted: %d, Rules upserted: %d",
                    provider_type,
                    provider_probe_upserts,
                    provider_rule_upserts,
                )

            # Log overall summary
            logger.info(
                "Guardrails seeding completed - Total probes upserted: %d, Total rules upserted: %d",
                probe_upserts,
                rule_upserts,
            )

        except FileNotFoundError as e:
            logger.exception("File not found during Guardrails seeding: %s", e)
            raise SeederException("File not found during Guardrails seeding") from e
        except json.JSONDecodeError as e:
            logger.exception("JSON decoding error during Guardrails seeding: %s", e)
            raise SeederException("JSON decoding error during Guardrails seeding") from e
        except Exception as e:
            logger.exception("Unexpected error during Guardrails seeding: %s", e)
            raise SeederException("Unexpected error during Guardrails seeding") from e


if __name__ == "__main__":
    import asyncio

    asyncio.run(GuardrailsSeeder().seed())


# python -m budconnect.seeders.guardrails
