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

"""Authentication schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for User."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    is_admin: bool = False


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    modified_at: datetime


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload."""

    user_id: str
    username: str
    is_admin: bool = False
    exp: Optional[datetime] = None


class PasswordChange(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordReset(BaseModel):
    """Schema for password reset."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
