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

"""Authentication services for user management and token handling."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from fastapi import status
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext

from ..commons.config import app_settings
from .crud import UserCRUD
from .models import User
from .schemas import TokenData, UserCreate, UserResponse


logger = logging.get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and user management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=app_settings.jwt_access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, app_settings.jwt_secret_key, algorithm=app_settings.jwt_algorithm)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token.

        Args:
            data: Data to encode in the token

        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=app_settings.jwt_refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, app_settings.jwt_secret_key, algorithm=app_settings.jwt_algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> TokenData:
        """Verify and decode a JWT token.

        Args:
            token: JWT token to verify
            token_type: Type of token ("access" or "refresh")

        Returns:
            TokenData with decoded information

        Raises:
            ClientException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, app_settings.jwt_secret_key, algorithms=[app_settings.jwt_algorithm])

            # Check token type for refresh tokens
            if token_type == "refresh" and payload.get("type") != "refresh":
                raise ClientException(message="Invalid token type", status_code=status.HTTP_401_UNAUTHORIZED)

            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            is_admin: bool = payload.get("is_admin", False)

            if user_id is None or username is None:
                raise ClientException(message="Invalid token payload", status_code=status.HTTP_401_UNAUTHORIZED)

            return TokenData(user_id=user_id, username=username, is_admin=is_admin)
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise ClientException(
                message="Could not validate credentials", status_code=status.HTTP_401_UNAUTHORIZED
            ) from e

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        with UserCRUD() as crud:
            # Try to find user by username
            user = crud.get_by_username(username)

            # If not found by username, try by email
            if not user:
                user = crud.get_by_email(username)

            if not user:
                return None

            if not AuthService.verify_password(password, user.hashed_password):
                return None

            if not user.is_active:
                logger.warning(f"Inactive user attempted login: {username}")
                return None

            return user

    @staticmethod
    def create_user(user_data: UserCreate) -> UserResponse:
        """Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user response

        Raises:
            ClientException: If username or email already exists
        """
        with UserCRUD() as crud:
            # Check if username already exists
            if crud.get_by_username(user_data.username):
                raise ClientException(message="Username already registered", status_code=status.HTTP_400_BAD_REQUEST)

            # Check if email already exists
            if crud.get_by_email(user_data.email):
                raise ClientException(message="Email already registered", status_code=status.HTTP_400_BAD_REQUEST)

            # Hash the password
            hashed_password = AuthService.hash_password(user_data.password)

            # Create the user
            user_dict = {
                "username": user_data.username,
                "email": user_data.email,
                "hashed_password": hashed_password,
                "is_admin": user_data.is_admin,
                "is_active": True,
            }

            created_user = crud.insert(user_dict)

            if not created_user:
                raise ClientException(
                    message="Failed to create user", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return UserResponse(
                id=created_user.id,
                username=created_user.username,
                email=created_user.email,
                is_active=created_user.is_active,
                is_admin=created_user.is_admin,
                created_at=created_user.created_at,
                modified_at=created_user.modified_at,
            )

    @staticmethod
    def get_current_user(user_id: str) -> User:
        """Get the current user by ID.

        Args:
            user_id: User ID from JWT token

        Returns:
            User object

        Raises:
            ClientException: If user not found or inactive
        """
        with UserCRUD() as crud:
            user = crud.get_by_id(UUID(user_id))

            if not user:
                raise ClientException(message="User not found", status_code=status.HTTP_404_NOT_FOUND)

            if not user.is_active:
                raise ClientException(message="Inactive user", status_code=status.HTTP_403_FORBIDDEN)

            return user

    @staticmethod
    def change_password(user_id: UUID, current_password: str, new_password: str) -> bool:
        """Change a user's password.

        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True if password changed successfully

        Raises:
            ClientException: If current password is incorrect
        """
        with UserCRUD() as crud:
            user = crud.get_by_id(user_id)

            if not user:
                raise ClientException(message="User not found", status_code=status.HTTP_404_NOT_FOUND)

            if not AuthService.verify_password(current_password, user.hashed_password):
                raise ClientException(message="Incorrect password", status_code=status.HTTP_400_BAD_REQUEST)

            hashed_password = AuthService.hash_password(new_password)
            return crud.update_password(user_id, hashed_password)
