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

"""User model for authentication."""

from budmicroframe.shared.psql_service import PSQLBase, TimestampMixin
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID


class User(PSQLBase, TimestampMixin):
    """User model for authentication and authorization.

    Attributes:
        id: Unique identifier for the user
        username: Unique username for login
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active
        is_admin: Whether the user has admin privileges
        created_at: Timestamp when user was created
        modified_at: Timestamp when user was last modified
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        """Return string representation of User."""
        return f"<User(username='{self.username}', email='{self.email}', is_admin={self.is_admin})>"
