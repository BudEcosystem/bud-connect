"""A2A Registry seeder — fetches standard agents from a2aregistry.org on startup."""

import logging

from ..a2a_registry.services import A2ARegistryService
from .base import BaseSeeder


logger = logging.getLogger(__name__)


class A2ARegistrySeeder(BaseSeeder):
    """Seeds the database with A2A agents from a2aregistry.org."""

    async def seed(self) -> None:
        """Seed the database with A2A registry agents."""
        logger.info("Starting A2A registry seeder...")
        try:
            summary = await A2ARegistryService.sync()
            logger.info(
                "A2A registry seeder completed: fetched=%d, upserted=%d, deleted=%d",
                summary.get("fetched", 0),
                summary.get("upserted", 0),
                summary.get("deleted", 0),
            )
        except Exception as e:
            logger.exception("Failed to seed A2A registry: %s", e)
            raise
