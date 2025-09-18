#!/usr/bin/env python3
"""Script to create initial admin user."""

import asyncio
import sys
from pathlib import Path


# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from budconnect.auth.crud import UserCRUD
from budconnect.auth.services import AuthService
from budconnect.commons.config import app_settings


async def create_admin():
    """Create initial admin user."""
    try:
        with UserCRUD() as crud:
            # Check if admin already exists
            existing_user = crud.get_by_username(app_settings.initial_admin_username)
            if existing_user:
                print(f"Admin user '{app_settings.initial_admin_username}' already exists")
                return

            # Create initial admin user
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
                print(f"Created admin user: {admin_user.username} (ID: {admin_user.id})")
                print(f"Email: {admin_user.email}")
                print(f"Password: {app_settings.initial_admin_password}")
                print("\nIMPORTANT: Please change the admin password after first login!")
            else:
                print("Failed to create admin user")
                sys.exit(1)

    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_admin())
