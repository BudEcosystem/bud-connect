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

"""User seeder for creating initial admin user."""

import logging

from budmicroframe.commons.exceptions import ClientException

from ..auth.crud import UserCRUD
from ..auth.services import AuthService
from ..commons.config import app_settings
from .base import BaseSeeder


logger = logging.getLogger(__name__)


class UserSeeder(BaseSeeder):
    """Seeder for creating initial admin user."""

    def __init__(self) -> None:
        """Initialize the user seeder."""
        super().__init__()

    async def seed(self) -> None:
        """Seed initial admin user if no users exist.

        Returns:
            Dictionary with seeding results
        """
        logger.info("Starting user seeder...")

        try:
            with UserCRUD() as crud:
                # Check if any users exist
                users, total = crud.list_users(limit=1)

                if total > 0:
                    logger.info("Users already exist, skipping initial admin creation")
                    logger.info("Users already exist - skipping initial admin user creation")
                    return

                # Create initial admin user from config
                hashed_password = AuthService.hash_password(app_settings.initial_admin_password)

                admin_data = {
                    "username": app_settings.initial_admin_username,
                    "email": app_settings.initial_admin_email,
                    "hashed_password": hashed_password,
                    "is_admin": True,
                    "is_active": True,
                }

                admin_user = crud.insert(admin_data)

                if admin_user:
                    logger.info(f"Created initial admin user: {admin_user.username}")
                    logger.info(f"Created initial admin user: {admin_user.username} (ID: {admin_user.id})")
                    return
                else:
                    logger.error("Failed to create initial admin user")
                    logger.error("Failed to create initial admin user")
                    return

        except ClientException as e:
            logger.error(f"Client error in user seeder: {e.message}")
            logger.error(f"Client error: {e.message}")
            return
        except Exception as e:
            logger.error(f"Unexpected error in user seeder: {str(e)}")
            logger.error(f"Unexpected error: {str(e)}")
            return
