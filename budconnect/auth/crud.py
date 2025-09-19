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

"""CRUD operations for User model."""

from typing import Optional
from uuid import UUID

from budmicroframe.shared.psql_service import CRUDMixin

from .models import User


class UserCRUD(CRUDMixin[User, None, None]):
    """CRUD operations for User model.

    This class provides create, read, update, and delete operations for the User model,
    which handles authentication and authorization.
    """

    __model__ = User

    def __init__(self) -> None:
        """Initialize UserCRUD with the User model."""
        super().__init__(model=User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: The username to search for

        Returns:
            User object if found, None otherwise
        """
        result = self.fetch_one(conditions={"username": username})
        return result

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: The email to search for

        Returns:
            User object if found, None otherwise
        """
        result = self.fetch_one(conditions={"email": email})
        return result

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user ID to search for

        Returns:
            User object if found, None otherwise
        """
        result = self.fetch_one(conditions={"id": str(user_id)})
        return result

    def update_password(self, user_id: UUID, hashed_password: str) -> bool:
        """Update a user's password.

        Args:
            user_id: The user ID
            hashed_password: The new hashed password

        Returns:
            True if update was successful, False otherwise
        """
        updated = self.update(conditions={"id": str(user_id)}, data={"hashed_password": hashed_password})
        return updated is not None

    def update_user(self, user_id: UUID, data: dict) -> Optional[User]:
        """Update a user's information.

        Args:
            user_id: The user ID
            data: Dictionary of fields to update

        Returns:
            Updated User object if successful, None otherwise
        """
        updated = self.update(conditions={"id": str(user_id)}, data=data)
        return updated

    def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate a user account.

        Args:
            user_id: The user ID to deactivate

        Returns:
            True if deactivation was successful, False otherwise
        """
        updated = self.update(conditions={"id": str(user_id)}, data={"is_active": False})
        return updated is not None

    def list_users(self, offset: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> tuple:
        """List users with optional filtering.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (optional)

        Returns:
            Tuple of (list of users, total count)
        """
        conditions = {}
        if is_active is not None:
            conditions["is_active"] = is_active

        result = self.fetch_many(conditions=conditions, offset=offset, limit=limit)

        # Handle tuple return from fetch_many
        if isinstance(result, tuple):
            users = result[0] if result else []
            # Get total count
            total_result = self.fetch_many(conditions=conditions)
            if isinstance(total_result, tuple):
                total = len(total_result[0]) if total_result else 0
            else:
                total = len(total_result) if total_result else 0
        else:
            users = result if result else []
            total = len(users)

        return users, total
