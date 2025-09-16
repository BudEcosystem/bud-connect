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

"""Authentication routes for user management and login."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing_extensions import Annotated

from .dependencies import get_current_active_user, get_current_admin_user
from .models import User
from .schemas import (
    PasswordChange,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from .services import AuthService


logger = logging.get_logger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, current_admin: Annotated[User, Depends(get_current_admin_user)]
) -> UserResponse:
    """Register a new user (admin only).

    Args:
        user_data: User registration data
        current_admin: Current admin user (dependency)

    Returns:
        Created user information
    """
    try:
        user = AuthService.create_user(user_data)
        logger.info(f"New user registered: {user.username} by admin: {current_admin.username}")
        return user
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e


@auth_router.post("/setup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def initial_setup(user_data: UserCreate) -> UserResponse:
    """Create first admin user (only works if no users exist).

    Args:
        user_data: Admin user registration data

    Returns:
        Created admin user information
    """
    from .crud import UserCRUD

    # Check if any users exist
    with UserCRUD() as crud:
        users, total = crud.list_users(limit=1)
        if total > 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Initial setup already completed")

    # Force admin flag for initial user
    user_data.is_admin = True

    try:
        user = AuthService.create_user(user_data)
        logger.info(f"Initial admin user created: {user.username}")
        return user
    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e


@auth_router.post("/login", response_model=Token)
async def login(user_data: UserLogin) -> Token:
    """Authenticate user and return access token.

    Args:
        user_data: Login credentials

    Returns:
        Access and refresh tokens
    """
    user = AuthService.authenticate_user(user_data.username, user_data.password)

    if not user:
        logger.warning(f"Failed login attempt for: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username, "is_admin": user.is_admin}
    )

    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id), "username": user.username})

    logger.info(f"User logged in: {user.username}")

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str) -> Token:
    """Refresh access token using refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        New access token
    """
    try:
        token_data = AuthService.verify_token(refresh_token, token_type="refresh")
        user = AuthService.get_current_user(token_data.user_id)

        # Create new access token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "username": user.username, "is_admin": user.is_admin}
        )

        return Token(access_token=access_token, token_type="bearer")
    except ClientException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_active_user)]) -> UserResponse:
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        modified_at=current_user.modified_at,
    )


@auth_router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange, current_user: Annotated[User, Depends(get_current_active_user)]
) -> None:
    """Change current user's password.

    Args:
        password_data: Current and new password
        current_user: Current authenticated user

    Returns:
        No content on success
    """
    try:
        success = AuthService.change_password(
            UUID(str(current_user.id)), password_data.current_password, password_data.new_password
        )

        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to change password")

        logger.info(f"Password changed for user: {current_user.username}")

    except ClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e


@auth_router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
) -> List[UserResponse]:
    """List all users (admin only).

    Args:
        page: Page number
        page_size: Number of items per page
        is_active: Optional filter by active status
        current_admin: Current admin user

    Returns:
        List of users
    """
    from .crud import UserCRUD

    offset = (page - 1) * page_size

    with UserCRUD() as crud:
        users, total = crud.list_users(offset=offset, limit=page_size, is_active=is_active)

        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                modified_at=user.modified_at,
            )
            for user in users
        ]


@auth_router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, user_update: UserUpdate, current_admin: Annotated[User, Depends(get_current_admin_user)]
) -> UserResponse:
    """Update user information (admin only).

    Args:
        user_id: User ID to update
        user_update: Update data
        current_admin: Current admin user

    Returns:
        Updated user information
    """
    from uuid import UUID

    from .crud import UserCRUD

    with UserCRUD() as crud:
        # Prepare update data
        update_data: Dict[str, Any] = {}
        if user_update.email is not None:
            update_data["email"] = user_update.email
        if user_update.is_active is not None:
            update_data["is_active"] = user_update.is_active
        if user_update.is_admin is not None:
            update_data["is_admin"] = user_update.is_admin

        updated_user = crud.update_user(UUID(user_id), update_data)

        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        logger.info(f"User {updated_user.username} updated by admin: {current_admin.username}")

        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            is_active=updated_user.is_active,
            is_admin=updated_user.is_admin,
            created_at=updated_user.created_at,
            modified_at=updated_user.modified_at,
        )


@auth_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(user_id: str, current_admin: Annotated[User, Depends(get_current_admin_user)]) -> None:
    """Deactivate a user (admin only).

    Args:
        user_id: User ID to deactivate
        current_admin: Current admin user

    Returns:
        No content on success
    """
    from uuid import UUID

    from .crud import UserCRUD

    with UserCRUD() as crud:
        success = crud.deactivate_user(UUID(user_id))

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        logger.info(f"User {user_id} deactivated by admin: {current_admin.username}")
