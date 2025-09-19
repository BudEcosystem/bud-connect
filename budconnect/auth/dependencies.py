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

"""FastAPI dependencies for authentication."""

from typing import Optional

from budmicroframe.commons.exceptions import ClientException
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing_extensions import Annotated

from .models import User
from .services import AuthService


# Security scheme for JWT Bearer tokens
security = HTTPBearer()


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> User:
    """Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Current authenticated User object

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token_data = AuthService.verify_token(credentials.credentials)
        user = AuthService.get_current_user(token_data.user_id)
        return user
    except ClientException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get the current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current active User object

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


async def get_current_admin_user(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    """Get the current admin user.

    Args:
        current_user: Current active user

    Returns:
        Current admin User object

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user


async def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> Optional[User]:
    """Get the current user if authenticated, None otherwise.

    This dependency is useful for endpoints that can work both
    authenticated and unauthenticated, but may provide different
    functionality based on authentication status.

    Args:
        credentials: Optional HTTP Bearer token credentials

    Returns:
        Current authenticated User object or None
    """
    if not credentials:
        return None

    try:
        token_data = AuthService.verify_token(credentials.credentials)
        user = AuthService.get_current_user(token_data.user_id)
        return user
    except ClientException:
        return None
