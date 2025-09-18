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

"""ModelInfo, Provider CRUD operations."""

from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.shared.psql_service import CRUDMixin, DBCreateSchemaType, ModelType
from sqlalchemy import and_, distinct, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..commons.constants import ProviderCapabilityEnum
from .models import License, ModelDetails, ModelInfo, Provider, engine_version_model_info, engine_version_provider


logger = logging.get_logger(__name__)


class ProviderCRUD(CRUDMixin[Provider, None, None]):
    __model__ = Provider

    def __init__(self) -> None:
        """Initialize the ProviderCRUD class.

        This constructor initializes the ProviderCRUD class by calling the parent
        CRUDMixin constructor with the Provider model. The ProviderCRUD class provides
        database operations for the Provider model.
        """
        super().__init__(self.__model__)

    def upsert(
        self,
        data: Union[DBCreateSchemaType, ModelType, Dict[str, Any]],
        conflict_target: Optional[List[str]] = None,
        session: Optional[Session] = None,
        raise_on_error: bool = True,
    ) -> UUID:
        """Perform an upsert (insert or update) operation on the database.

        This method inserts a new record if it doesn't exist, or updates an existing record
        if it does, based on the specified conflict target columns. It handles different
        input data types and manages database transaction details.

        Args:
            data: The data to insert or update. Can be a dictionary, a Pydantic schema,
                or a SQLAlchemy model instance.
            conflict_target: A list of column names to check for conflicts. These should
                typically be columns with unique constraints. If None, performs a regular
                insert with no conflict handling.
            session: An existing SQLAlchemy session to use. If None, a new session will
                be created and closed after the operation.
            raise_on_error: If True, raises a ValueError when an SQLAlchemy error occurs.
                If False, errors are logged but not raised.

        Raises:
            ValueError: If the data type is invalid or if the upsert operation fails and
                raise_on_error is True.
            SQLAlchemyError: If a database error occurs and is not caught.
        """
        _session = session or self.get_session()
        try:
            if isinstance(data, (type(DBCreateSchemaType), self.model, dict)):
                obj: Dict[str, Any] = data.copy() if isinstance(data, dict) else data.model_dump(exclude_unset=True)
            else:
                raise ValueError("Invalid data type for upsert")

            stmt = insert(self.model.__table__).values(obj)
            if conflict_target:
                stmt = stmt.on_conflict_do_update(index_elements=conflict_target, set_=obj)

            stmt = stmt.returning(self.model.id)
            result = _session.execute(stmt)
            _session.commit()
            logger.debug("Upsert operation successful on %s", self.model.__tablename__)

            row = result.first()
            if row:
                # row[0] is the ID directly when using returning(self.model.id)
                return UUID(str(row[0]))  # Ensure we return a UUID

            # If no row returned (shouldn't happen but handle gracefully)
            # Try to fetch the existing row using conflict target
            if conflict_target and len(conflict_target) > 0:
                filter_dict = {key: obj.get(key) for key in conflict_target if key in obj}
                existing = _session.query(self.model).filter_by(**filter_dict).first()
                if existing and hasattr(existing, "id"):
                    return UUID(str(existing.id))

            raise ValueError("No result returned from upsert operation")
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to upsert data in %s: %s", self.model.__tablename__, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to upsert data in {self.model.__tablename__}") from e
            return UUID("00000000-0000-0000-0000-000000000000")  # Return a null UUID on error
        finally:
            self.cleanup_session(_session if session is None else None)

    def add_engine_version(
        self,
        provider_id: UUID,
        engine_version_id: UUID,
        session: Optional[Session] = None,
        raise_on_error: bool = True,
    ) -> None:
        """Add engine versions to a provider.

        Args:
            provider_id: The ID of the provider to add the engine version to.
            version_ids: The IDs of the engine versions to add to the provider.
            session: The session to use for the query.
            raise_on_error: Whether to raise an error if the operation fails.
        """
        _session = session or self.get_session()
        try:
            stmt = (
                insert(engine_version_provider)
                .values(provider_id=provider_id, engine_version_id=engine_version_id)
                .on_conflict_do_nothing()
                .returning(engine_version_provider.c.provider_id, engine_version_provider.c.engine_version_id)
            )
            _session.execute(stmt)
            _session.commit()
            logger.debug("Added engine version %s to provider %s", engine_version_id, provider_id)
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to add engine versions to provider %s: %s", provider_id, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to add engine versions to provider {provider_id}") from e
        finally:
            self.cleanup_session(_session if session is None else None)

    def get_compatible_providers(
        self, version_id: UUID, offset: int, limit: int, session: Optional[Session] = None
    ) -> Tuple[int, List[Provider]]:
        """Get the compatible providers for a given engine version.

        Args:
            version_id: The ID of the engine version to get compatible providers for.
            offset: The offset to start the pagination from.
            limit: The number of providers to return.
            session: The session to use for the query.

        Returns:
            A list of compatible providers.
        """
        _session = session or self.get_session()

        # Get total count of providers
        total_providers = (
            _session.query(func.count(distinct(Provider.id)))
            .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
            .filter(engine_version_provider.c.engine_version_id == version_id)
            .scalar()
        )

        # Get all providers and their models in a single query
        query = (
            _session.query(Provider, ModelInfo)
            .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
            .outerjoin(  # Use outerjoin to include providers with no models
                engine_version_model_info, engine_version_model_info.c.engine_version_id == version_id
            )
            .outerjoin(
                ModelInfo,
                and_(ModelInfo.id == engine_version_model_info.c.model_info_id, ModelInfo.provider_id == Provider.id),
            )
            .filter(engine_version_provider.c.engine_version_id == version_id)
            .order_by(Provider.provider_type)
        )

        # Get distinct providers for pagination
        provider_ids = [
            p.id
            for p in _session.query(Provider.id)
            .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
            .filter(engine_version_provider.c.engine_version_id == version_id)
            .order_by(Provider.name)
            .offset(offset)
            .limit(limit)
        ]

        # Filter the main query by paginated provider IDs
        query = query.filter(Provider.id.in_(provider_ids))

        # Execute query
        results = query.all()

        return total_providers, results

    def get_providers_by_capability(
        self,
        version_id: UUID,
        capability: ProviderCapabilityEnum,
        offset: int,
        limit: int,
        session: Optional[Session] = None,
    ) -> Tuple[int, List[Provider]]:
        """Get providers that have a specific capability and are compatible with the engine version.

        Args:
            version_id: The ID of the engine version to get compatible providers for.
            capability: The capability to filter providers by.
            offset: The offset to start the pagination from.
            limit: The number of providers to return.
            session: The session to use for the query.

        Returns:
            A tuple containing the total count and list of providers with the specified capability.
        """
        _session = session or self.get_session()
        try:
            # Base query for providers with the specified capability that are compatible with the engine version
            base_query = (
                _session.query(Provider)
                .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
                .filter(engine_version_provider.c.engine_version_id == version_id)
                .filter(func.array_to_string(Provider.capabilities, ",").contains(capability.name))
                .distinct()
            )

            # Get total count
            total_count = base_query.count()

            # Get paginated results
            providers = base_query.order_by(Provider.name).offset(offset).limit(limit).all()

            return total_count, providers
        finally:
            self.cleanup_session(_session if session is None else None)

    def get_compatible_providers_with_capability(
        self,
        version_id: UUID,
        capability: ProviderCapabilityEnum,
        offset: int,
        limit: int,
        session: Optional[Session] = None,
    ) -> Tuple[int, List[Tuple[Provider, Optional[ModelInfo]]]]:
        """Get providers with a specific capability and their models for a given engine version.

        Args:
            version_id: The ID of the engine version to get compatible providers for.
            capability: The capability to filter providers by.
            offset: The offset to start the pagination from.
            limit: The number of providers to return.
            session: The session to use for the query.

        Returns:
            A tuple of (total_count, list of (provider, model) tuples).
        """
        _session = session or self.get_session()
        try:
            # Get total count of providers with the capability
            total_providers = (
                _session.query(func.count(distinct(Provider.id)))
                .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
                .filter(engine_version_provider.c.engine_version_id == version_id)
                .filter(func.array_to_string(Provider.capabilities, ",").contains(capability.name))
                .scalar()
            )

            # Get all providers and their models in a single query
            query = (
                _session.query(Provider, ModelInfo)
                .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
                .filter(func.array_to_string(Provider.capabilities, ",").contains(capability.name))
                .outerjoin(  # Use outerjoin to include providers with no models
                    engine_version_model_info, engine_version_model_info.c.engine_version_id == version_id
                )
                .outerjoin(
                    ModelInfo,
                    and_(
                        ModelInfo.id == engine_version_model_info.c.model_info_id, ModelInfo.provider_id == Provider.id
                    ),
                )
                .filter(engine_version_provider.c.engine_version_id == version_id)
                .order_by(Provider.provider_type)
            )

            # Get distinct providers for pagination
            provider_ids = [
                p.id
                for p in _session.query(Provider.id)
                .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
                .filter(engine_version_provider.c.engine_version_id == version_id)
                .filter(func.array_to_string(Provider.capabilities, ",").contains(capability.name))
                .order_by(Provider.name)
                .offset(offset)
                .limit(limit)
            ]

            # Filter the main query by paginated provider IDs
            query = query.filter(Provider.id.in_(provider_ids))

            # Execute query
            results = query.all()

            return total_providers, results
        finally:
            self.cleanup_session(_session if session is None else None)


class LicenseCRUD(CRUDMixin[License, None, None]):
    __model__ = License

    def __init__(self) -> None:
        """Initialize the LicenseCRUD class.

        This constructor initializes the LicenseCRUD class by calling the parent
        CRUDMixin constructor with the License model. The LicenseCRUD class provides
        database operations for the License model.
        """
        super().__init__(self.__model__)

    def upsert(
        self,
        data: Union[DBCreateSchemaType, ModelType, Dict[str, Any]],
        conflict_target: Optional[List[str]] = None,
        session: Optional[Session] = None,
        raise_on_error: bool = True,
    ) -> UUID:
        """Create or update a license.

        This method creates a new license or updates an existing license if a conflict
        occurs on the specified columns. The upsert operation is atomic and ensures
        data consistency.

        Args:
            data: The data to upsert. Can be a Pydantic schema, model instance, or dictionary.
            conflict_target: List of column names to check for conflicts. Defaults to ["key"].
            session: Optional database session. If None, a new session will be created.
            raise_on_error: Whether to raise an exception on error. Defaults to True.

        Returns:
            UUID: The ID of the created or updated license.

        Raises:
            ValueError: If the data type is invalid or the operation fails.
            SQLAlchemyError: If a database error occurs and raise_on_error is True.
        """
        # Default to conflict on 'key' column for licenses
        if conflict_target is None:
            conflict_target = ["key"]

        _session = session or self.get_session()
        try:
            if isinstance(data, dict):
                obj = data
            elif hasattr(data, "model_dump"):
                obj = data.model_dump()
            elif hasattr(data, "__dict__"):
                obj = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
            else:
                raise ValueError("Invalid data type for upsert")

            stmt = insert(self.model.__table__).values(obj)
            if conflict_target:
                stmt = stmt.on_conflict_do_update(index_elements=conflict_target, set_=obj)

            stmt = stmt.returning(self.model)
            result = _session.execute(stmt)
            _session.commit()
            logger.debug("Upsert operation successful on %s", self.model.__tablename__)

            row = result.first()
            if row:
                # Handle both ORM model instances and Row objects
                if hasattr(row, "id"):
                    # Direct model instance
                    return UUID(str(row.id))
                elif hasattr(row, "_mapping") and "id" in row._mapping:
                    # SQLAlchemy Row object
                    return UUID(str(row._mapping["id"]))
                elif len(row) > 0 and hasattr(row[0], "id"):
                    # Tuple with model instance
                    return UUID(str(row[0].id))

            # For upserts, try to fetch the record if returning didn't work
            if conflict_target and "id" in obj:
                return UUID(str(obj["id"]))

            raise ValueError("No result returned from upsert operation")
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to upsert data in %s: %s", self.model.__tablename__, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to upsert data in {self.model.__tablename__}") from e
            return UUID("00000000-0000-0000-0000-000000000000")
        finally:
            self.cleanup_session(_session if session is None else None)


class ModelInfoCRUD(CRUDMixin[ModelInfo, None, None]):
    __model__ = ModelInfo

    def __init__(self) -> None:
        """Initialize the ProviderCRUD class.

        This constructor initializes the ProviderCRUD class by calling the parent
        CRUDMixin constructor with the Provider model. The ProviderCRUD class provides
        database operations for the Provider model.
        """
        super().__init__(self.__model__)

    def upsert(
        self,
        data: Union[DBCreateSchemaType, ModelType, Dict[str, Any]],
        conflict_target: Optional[List[str]] = None,
        session: Optional[Session] = None,
        raise_on_error: bool = True,
    ) -> UUID:
        """Perform an upsert (insert or update) operation on the database.

        This method inserts a new record if it doesn't exist, or updates an existing record
        if it does, based on the specified conflict target columns. It handles different
        input data types and manages database transaction details.

        Args:
            data: The data to insert or update. Can be a dictionary, a Pydantic schema,
                or a SQLAlchemy model instance.
            conflict_target: A list of column names to check for conflicts. These should
                typically be columns with unique constraints. If None, performs a regular
                insert with no conflict handling.
            session: An existing SQLAlchemy session to use. If None, a new session will
                be created and closed after the operation.
            raise_on_error: If True, raises a ValueError when an SQLAlchemy error occurs.
                If False, errors are logged but not raised.

        Raises:
            ValueError: If the data type is invalid or if the upsert operation fails and
                raise_on_error is True.
            SQLAlchemyError: If a database error occurs and is not caught.
        """
        _session = session or self.get_session()
        try:
            if isinstance(data, (type(DBCreateSchemaType), self.model, dict)):
                obj: Dict[str, Any] = data.copy() if isinstance(data, dict) else data.model_dump(exclude_unset=True)
            else:
                raise ValueError("Invalid data type for upsert")

            stmt = insert(self.model.__table__).values(obj)
            if conflict_target:
                stmt = stmt.on_conflict_do_update(index_elements=conflict_target, set_=obj)

            stmt = stmt.returning(self.model.id)
            result = _session.execute(stmt)
            _session.commit()
            logger.debug("Upsert operation successful on %s", self.model.__tablename__)

            row = result.first()
            if row:
                # row[0] is the ID directly when using returning(self.model.id)
                return UUID(str(row[0]))  # Ensure we return a UUID

            # If no row returned (shouldn't happen but handle gracefully)
            # Try to fetch the existing row using conflict target
            if conflict_target and len(conflict_target) > 0:
                filter_dict = {key: obj.get(key) for key in conflict_target if key in obj}
                existing = _session.query(self.model).filter_by(**filter_dict).first()
                if existing and hasattr(existing, "id"):
                    return UUID(str(existing.id))

            raise ValueError("No result returned from upsert operation")
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to upsert data in %s: %s", self.model.__tablename__, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to upsert data in {self.model.__tablename__}") from e
            return UUID("00000000-0000-0000-0000-000000000000")  # Return a null UUID on error
        finally:
            self.cleanup_session(_session if session is None else None)

    def add_engine_version(
        self,
        model_info_id: UUID,
        engine_version_id: UUID,
        session: Optional[Session] = None,
        raise_on_error: bool = True,
    ) -> None:
        """Add engine versions to a provider.

        Args:
            model_info_id: The ID of the model info to add the engine version to.
            engine_version_id: The IDs of the engine versions to add to the model info.
            session: The session to use for the query.
            raise_on_error: Whether to raise an error if the operation fails.
        """
        _session = session or self.get_session()
        try:
            stmt = (
                insert(engine_version_model_info)
                .values(model_info_id=model_info_id, engine_version_id=engine_version_id)
                .on_conflict_do_nothing()
                .returning(engine_version_model_info.c.model_info_id, engine_version_model_info.c.engine_version_id)
            )
            _session.execute(stmt)
            _session.commit()
            logger.debug("Added engine version %s to model info %s", engine_version_id, model_info_id)
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to add engine versions to model info %s: %s", model_info_id, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to add engine versions to model info {model_info_id}") from e
        finally:
            self.cleanup_session(_session if session is None else None)


class ModelDetailsCRUD(CRUDMixin[ModelDetails, None, None]):
    __model__ = ModelDetails

    def __init__(self) -> None:
        """Initialize the ModelDetailsCRUD class.

        This constructor initializes the ModelDetailsCRUD class by calling the parent
        CRUDMixin constructor with the ModelDetails model. The ModelDetailsCRUD class provides
        database operations for the ModelDetails model.
        """
        super().__init__(self.__model__)

    def get_by_model_uri(self, model_uri: str, session: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """Get model details with model info and provider by model URI.

        Args:
            model_uri: The URI of the model to get details for.
            session: The session to use for the query.

        Returns:
            A dictionary containing model details, model info, and provider if found, None otherwise.
        """
        _session = session or self.get_session()
        try:
            # Join with ModelInfo and Provider to get all data
            result = (
                _session.query(
                    self.model,
                    ModelInfo,
                    Provider.name.label("provider_name"),
                    Provider.provider_type.label("provider_type"),
                )
                .join(ModelInfo, self.model.model_info_id == ModelInfo.id)
                .join(Provider, ModelInfo.provider_id == Provider.id)
                .filter(ModelInfo.uri == model_uri)
                .first()
            )

            if result:
                model_details, model_info, provider_name, provider_type = result

                # Combine all data into a single dictionary
                combined_data = {
                    # ModelDetails fields
                    "id": model_details.id,
                    "model_info_id": model_details.model_info_id,
                    "description": model_details.description,
                    "advantages": model_details.advantages,
                    "disadvantages": model_details.disadvantages,
                    "use_cases": model_details.use_cases,
                    "evaluations": model_details.evaluations,
                    "languages": model_details.languages,
                    "tags": model_details.tags,
                    "tasks": model_details.tasks,
                    "papers": model_details.papers,
                    "github_url": model_details.github_url,
                    "website_url": model_details.website_url,
                    "logo_url": model_details.logo_url,
                    "architecture": model_details.architecture,
                    "model_tree": model_details.model_tree,
                    "extraction_metadata": model_details.extraction_metadata,
                    "created_at": model_details.created_at,
                    "modified_at": model_details.modified_at,
                    # ModelInfo fields
                    "uri": model_info.uri,
                    "modality": model_info.modality,
                    "input_cost": model_info.input_cost,
                    "output_cost": model_info.output_cost,
                    "cache_cost": model_info.cache_cost,
                    "search_context_cost_per_query": model_info.search_context_cost_per_query,
                    "tokens": model_info.tokens,
                    "rate_limits": model_info.rate_limits,
                    "media_limits": model_info.media_limits,
                    "features": model_info.features,
                    "endpoints": model_info.endpoints,
                    "deprecation_date": model_info.deprecation_date,
                    # Provider fields
                    "provider_name": provider_name,
                    "provider_type": provider_type,
                }

                return combined_data

            return None
        finally:
            self.cleanup_session(_session if session is None else None)
