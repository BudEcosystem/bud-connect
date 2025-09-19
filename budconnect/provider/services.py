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

"""Service layer for provider operations."""

import logging
from typing import List, Optional, Tuple
from uuid import UUID

from budmicroframe.commons.exceptions import ClientException
from sqlalchemy.exc import IntegrityError

from budconnect.model.crud import ProviderCRUD
from budconnect.model.models import Provider

from .schemas import ProviderCreate, ProviderUpdate


logger = logging.getLogger(__name__)


class ProviderService:
    """Service class for provider operations."""

    @staticmethod
    def get_all_providers(page: int = 1, page_size: int = 100, search: Optional[str] = None) -> Tuple[List[dict], int]:
        """Get all providers with pagination and optional search.

        Args:
            page: Page number (starts from 1)
            page_size: Number of items per page
            search: Optional search term for name or type

        Returns:
            Tuple of (list of provider dicts, total count)
        """
        from sqlalchemy import func

        from ..model.models import ModelInfo

        with ProviderCRUD() as crud:
            session = crud.get_session()
            try:
                # Build base query with model count using LEFT JOIN
                query = (
                    session.query(Provider, func.count(ModelInfo.id).label("model_count"))
                    .outerjoin(ModelInfo, Provider.id == ModelInfo.provider_id)
                    .group_by(Provider.id)
                )

                # Apply search filter if provided
                if search:
                    search_lower = f"%{search.lower()}%"
                    query = query.filter(
                        (func.lower(Provider.name).like(search_lower))
                        | (func.lower(Provider.provider_type).like(search_lower))
                    )

                # Get all results for total count
                all_results = query.all()
                total = len(all_results)

                # Apply pagination manually
                offset = (page - 1) * page_size
                paginated_results = all_results[offset : offset + page_size]

                # Convert to dict format
                result_providers = []
                for provider, model_count in paginated_results:
                    result_providers.append(
                        {
                            "id": provider.id,
                            "name": provider.name,
                            "provider_type": provider.provider_type,
                            "icon": provider.icon,
                            "description": provider.description,
                            "credentials": provider.credentials,
                            "created_at": provider.created_at,
                            "modified_at": provider.modified_at,
                            "model_count": model_count or 0,
                        }
                    )

                return result_providers, total
            finally:
                crud.cleanup_session(session)

    @staticmethod
    def get_provider_by_id(provider_id: UUID) -> Provider:
        """Get a provider by its ID.

        Args:
            provider_id: UUID of the provider

        Returns:
            Provider object

        Raises:
            ClientException: If provider not found
        """
        from sqlalchemy import func

        from ..model.models import ModelInfo

        with ProviderCRUD() as crud:
            session = crud.get_session()
            try:
                # Query provider with model count
                result = (
                    session.query(Provider, func.count(ModelInfo.id).label("model_count"))
                    .outerjoin(ModelInfo, Provider.id == ModelInfo.provider_id)
                    .filter(Provider.id == provider_id)
                    .group_by(Provider.id)
                    .first()
                )

                if not result:
                    raise ClientException(message=f"Provider with ID {provider_id} not found", status_code=404)

                provider, model_count = result
                provider.model_count = model_count or 0
                return provider
            finally:
                crud.cleanup_session(session)

    @staticmethod
    def create_provider(provider_data: ProviderCreate) -> Provider:
        """Create a new provider.

        Args:
            provider_data: Provider creation data

        Returns:
            Created provider object

        Raises:
            ClientException: If provider_type already exists
        """
        with ProviderCRUD() as crud:
            # Check if provider_type already exists
            existing = crud.fetch_one({"provider_type": provider_data.provider_type})
            if existing:
                raise ClientException(
                    message=f"Provider with type '{provider_data.provider_type}' already exists", status_code=400
                )

            try:
                # Convert credentials to dict format
                credentials_dict = [cred.model_dump() for cred in provider_data.credentials]

                provider = crud.create(
                    {
                        "name": provider_data.name,
                        "provider_type": provider_data.provider_type,
                        "icon": provider_data.icon,
                        "description": provider_data.description,
                        "credentials": credentials_dict,
                    }
                )
                provider.model_count = 0
                return provider
            except IntegrityError as e:
                logger.error(f"Integrity error creating provider: {e}")
                raise ClientException(message="Failed to create provider due to data conflict", status_code=400) from e

    @staticmethod
    def update_provider(provider_id: UUID, update_data: ProviderUpdate) -> Provider:
        """Update an existing provider.

        Args:
            provider_id: UUID of the provider to update
            update_data: Update data (only provided fields will be updated)

        Returns:
            Updated provider object

        Raises:
            ClientException: If provider not found
        """
        with ProviderCRUD() as crud:
            # Check if provider exists
            provider = crud.fetch_one({"id": provider_id})
            if not provider:
                raise ClientException(message=f"Provider with ID {provider_id} not found", status_code=404)

            # Build update dict with only provided fields
            update_dict = {}
            if update_data.name is not None:
                update_dict["name"] = update_data.name
            if update_data.icon is not None:
                update_dict["icon"] = update_data.icon
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.credentials is not None:
                update_dict["credentials"] = [cred.model_dump() for cred in update_data.credentials]

            if update_dict:
                updated_provider = crud.update(provider, update_dict)
                # Get model count using a separate query
                from sqlalchemy import func

                from ..model.models import ModelInfo

                session = crud.get_session()
                try:
                    model_count = (
                        session.query(func.count(ModelInfo.id))
                        .filter(ModelInfo.provider_id == updated_provider.id)
                        .scalar()
                        or 0
                    )
                    updated_provider.model_count = model_count
                finally:
                    crud.cleanup_session(session)
                return updated_provider

            # Get model count for unchanged provider
            from sqlalchemy import func

            from ..model.models import ModelInfo

            session = crud.get_session()
            try:
                model_count = (
                    session.query(func.count(ModelInfo.id)).filter(ModelInfo.provider_id == provider.id).scalar() or 0
                )
                provider.model_count = model_count
            finally:
                crud.cleanup_session(session)
            return provider

    @staticmethod
    def delete_provider(provider_id: UUID) -> None:
        """Delete a provider.

        Args:
            provider_id: UUID of the provider to delete

        Raises:
            ClientException: If provider not found or has associated models
        """
        from sqlalchemy import func

        from ..model.models import ModelInfo

        with ProviderCRUD() as crud:
            session = crud.get_session()
            try:
                # Check if provider exists and count its models
                result = (
                    session.query(Provider, func.count(ModelInfo.id).label("model_count"))
                    .outerjoin(ModelInfo, Provider.id == ModelInfo.provider_id)
                    .filter(Provider.id == provider_id)
                    .group_by(Provider.id)
                    .first()
                )

                if not result:
                    raise ClientException(message=f"Provider with ID {provider_id} not found", status_code=404)

                provider, model_count = result
                if model_count > 0:
                    raise ClientException(
                        message=f"Cannot delete provider because it has {model_count} associated model{'s' if model_count > 1 else ''}. Delete all models first.",
                        status_code=400,
                    )

                # Now delete the provider (no models attached)
                crud.delete({"id": provider_id})
            except ClientException:
                # Re-raise client exceptions
                raise
            except ValueError as e:
                # The CRUDMixin wraps database errors in ValueError
                # Check if it's a foreign key violation by examining the error message
                error_msg = str(e).lower()
                if "foreign" in error_msg or "constraint" in error_msg or "reference" in error_msg:
                    # This is likely a foreign key constraint error
                    raise ClientException(
                        message="Cannot delete provider because it has associated models. Delete all models first.",
                        status_code=400,
                    ) from e
                # Re-raise other ValueErrors
                raise ClientException(message=str(e), status_code=500) from e
            except Exception as e:
                # Handle any other unexpected exceptions
                logger.error(f"Unexpected error deleting provider: {e}")
                raise ClientException(
                    message="An unexpected error occurred while deleting the provider", status_code=500
                ) from e
            finally:
                crud.cleanup_session(session)
