"""Model Architecture Seeder.

This module is responsible for seeding model architecture class data
into the database.
"""

import json
from pathlib import Path
from typing import Any, Dict, cast

from budmicroframe.commons.logging import get_logger
from sqlalchemy.dialects.postgresql import insert

from budconnect.model.crud import ModelArchitectureClassCRUD
from budconnect.model.models import ModelArchitectureClass

from .base import BaseSeeder


logger = get_logger(__name__)


class ModelArchitectureSeeder(BaseSeeder):
    """Handles seeding of model architecture data."""

    def __init__(self) -> None:
        """Initialize the seeder."""
        super().__init__()
        self.data_dir = Path(__file__).parent / "data"

    def load_architecture_data(self) -> Dict[str, Any]:
        """Load model architecture data from JSON file.

        Returns:
            Dictionary containing architecture data
        """
        architecture_file = self.data_dir / "model_architectures.json"
        with open(architecture_file, "r") as f:
            return cast(Dict[str, Any], json.load(f))

    async def seed(self) -> None:
        """Execute the model architecture seeding process.

        This method loads model architecture data from JSON and seeds it
        into the database using upsert operations.
        """
        try:
            logger.info("Starting model architecture seeding...")

            data = self.load_architecture_data()
            architectures = data.get("architectures", [])

            if not architectures:
                logger.warning("No architecture data found to seed")
                return

            # Prepare data for bulk insert/update
            architecture_records = []
            for arch in architectures:
                architecture_records.append(
                    {
                        "class_name": arch["class_name"],
                        "architecture_family": arch["architecture_family"],
                        "tool_calling_parser_type": arch.get("tool_calling_parser_type"),
                        "reasoning_parser_type": arch.get("reasoning_parser_type"),
                        "supports_lora": arch.get("supports_lora", False),
                        "supports_pipeline_parallelism": arch.get("supports_pipeline_parallelism", False),
                    }
                )

            # Use CRUD to manage the session
            crud = ModelArchitectureClassCRUD()
            with crud as crud:
                session = crud.get_session()
                # Use PostgreSQL's ON CONFLICT to handle updates
                stmt = insert(ModelArchitectureClass).values(architecture_records)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["class_name"],
                    set_={
                        "architecture_family": stmt.excluded.architecture_family,
                        "supports_lora": stmt.excluded.supports_lora,
                        "supports_pipeline_parallelism": stmt.excluded.supports_pipeline_parallelism,
                    },
                )

                session.execute(stmt)
                session.commit()
                logger.info(f"Successfully seeded {len(architecture_records)} model architectures")

            logger.info("Model architecture seeding completed successfully")

        except Exception as e:
            logger.error(f"Model architecture seeding failed: {e}")
            raise
