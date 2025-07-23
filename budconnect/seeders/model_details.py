"""Model Details Seeder for BudConnect.

This module handles seeding detailed model information into the database.
"""

import json
from pathlib import Path
from typing import Any, Dict

from budmicroframe.commons import logging
from sqlalchemy.dialects.postgresql import insert

from ..model.crud import ModelDetailsCRUD, ModelInfoCRUD
from ..model.models import ModelDetails, ModelInfo
from .base import BaseSeeder


logger = logging.get_logger(__name__)


class ModelDetailsSeeder(BaseSeeder):
    """Seeder for model details data."""

    def __init__(self) -> None:
        """Initialize the ModelDetailsSeeder."""
        super().__init__()
        self.data_file = Path(__file__).parent / "data" / "model_details.json"

    def load_data(self) -> Dict[str, Any]:
        """Load model details data from JSON file.

        Returns:
            Dict containing model details data.
        """
        if not self.data_file.exists():
            logger.warning(f"Model details data file not found: {self.data_file}")
            return {}

        with open(self.data_file, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data

    async def seed(self) -> None:
        """Seed model details data into the database."""
        logger.info("Starting model details seeding...")

        data = self.load_data()
        if not data:
            logger.warning("No model details data to seed")
            return

        # Get all model info records to map URI to ID
        model_info_crud = ModelInfoCRUD()
        model_details_crud = ModelDetailsCRUD()

        with model_info_crud as crud:
            session = crud.get_session()
            all_models = session.query(ModelInfo).all()
            uri_to_id = {model.uri: model.id for model in all_models}

        # Process each model detail
        seeded_count = 0
        with model_details_crud as crud:
            session = crud.get_session()

            for uri, details in data.items():
                model_info_id = uri_to_id.get(uri)
                if not model_info_id:
                    logger.warning(f"Model not found for URI: {uri}, skipping details")
                    continue

                try:
                    # Prepare model details data
                    model_details_data = {
                        "model_info_id": model_info_id,
                        "description": details.get("description"),
                        "advantages": details.get("advantages", []),
                        "disadvantages": details.get("disadvantages", []),
                        "use_cases": details.get("use_cases", []),
                        "evaluations": details.get("evaluations", []),
                        "languages": details.get("languages", []),
                        "tags": details.get("tags", []),
                        "tasks": details.get("tasks", []),
                        "papers": details.get("papers", []),
                        "github_url": details.get("github_url"),
                        "website_url": details.get("website_url"),
                        "logo_url": details.get("logo_url"),
                        "architecture": details.get("architecture"),
                        "model_tree": details.get("model_tree"),
                        "extraction_metadata": details.get("extraction_metadata"),
                    }

                    # Use upsert to handle existing records
                    stmt = insert(ModelDetails).values(model_details_data)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["model_info_id"],
                        set_={
                            "description": stmt.excluded.description,
                            "advantages": stmt.excluded.advantages,
                            "disadvantages": stmt.excluded.disadvantages,
                            "use_cases": stmt.excluded.use_cases,
                            "evaluations": stmt.excluded.evaluations,
                            "languages": stmt.excluded.languages,
                            "tags": stmt.excluded.tags,
                            "tasks": stmt.excluded.tasks,
                            "papers": stmt.excluded.papers,
                            "github_url": stmt.excluded.github_url,
                            "website_url": stmt.excluded.website_url,
                            "logo_url": stmt.excluded.logo_url,
                            "architecture": stmt.excluded.architecture,
                            "model_tree": stmt.excluded.model_tree,
                            "extraction_metadata": stmt.excluded.extraction_metadata,
                            "modified_at": stmt.excluded.modified_at,
                        },
                    )

                    session.execute(stmt)
                    seeded_count += 1
                    logger.debug(f"Seeded details for model: {uri}")

                except Exception as e:
                    logger.error(f"Error seeding details for model {uri}: {e}")
                    continue

            session.commit()
            logger.info(f"Successfully seeded {seeded_count} model details")

    async def cleanup(self) -> None:
        """Clean up model details data from the database."""
        logger.info("Starting model details cleanup...")

        model_details_crud = ModelDetailsCRUD()
        with model_details_crud as crud:
            session = crud.get_session()
            try:
                # Delete all model details
                deleted_count = session.query(ModelDetails).delete()
                session.commit()
                logger.info(f"Successfully deleted {deleted_count} model details")
            except Exception as e:
                session.rollback()
                logger.error(f"Error during model details cleanup: {e}")
                raise
