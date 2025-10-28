"""Model Architecture Seeder.

This module is responsible for seeding model architecture class data
into the database.
"""

import json
from pathlib import Path
from typing import Any, Dict, cast

from budmicroframe.commons.logging import get_logger
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from budconnect.model.models import ModelArchitectureClass


logger = get_logger(__name__)


class ModelArchitectureSeeder:
    """Handles seeding of model architecture data."""

    def __init__(self, session: Session):
        """Initialize the seeder with a database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.data_dir = Path(__file__).parent / "data"

    def load_architecture_data(self) -> Dict[str, Any]:
        """Load model architecture data from JSON file.

        Returns:
            Dictionary containing architecture data
        """
        architecture_file = self.data_dir / "model_architectures.json"
        with open(architecture_file, "r") as f:
            return cast(Dict[str, Any], json.load(f))

    def seed_architectures(self) -> None:
        """Seed model architecture class data into the database."""
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
                }
            )

        # Use PostgreSQL's ON CONFLICT to handle updates
        stmt = insert(ModelArchitectureClass).values(architecture_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["class_name"],
            set_={
                "architecture_family": stmt.excluded.architecture_family,
                "tool_calling_parser_type": stmt.excluded.tool_calling_parser_type,
                "reasoning_parser_type": stmt.excluded.reasoning_parser_type,
            },
        )

        try:
            self.session.execute(stmt)
            self.session.commit()
            logger.info(f"Successfully seeded {len(architecture_records)} model architectures")
        except Exception as e:
            logger.error(f"Error seeding model architectures: {e}")
            self.session.rollback()
            raise

    def run(self) -> None:
        """Execute the model architecture seeding process."""
        try:
            self.seed_architectures()
            logger.info("Model architecture seeding completed successfully")
        except Exception as e:
            logger.error(f"Model architecture seeding failed: {e}")
            raise


def seed_model_architectures(session: Session) -> None:
    """Seed model architectures from JSON data file.

    Args:
        session: SQLAlchemy database session
    """
    seeder = ModelArchitectureSeeder(session)
    seeder.run()
