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

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.shared.psql_service import CRUDMixin, DBCreateSchemaType, ModelType
from sqlalchemy import and_, distinct, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models import ModelInfo, Provider, engine_version_model_info, engine_version_provider


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
                obj: dict = data.copy() if isinstance(data, dict) else data.model_dump(exclude_unset=True)
            else:
                raise ValueError("Invalid data type for upsert")

            stmt = insert(self.model.__table__).values(obj)
            if conflict_target:
                stmt = stmt.on_conflict_do_update(index_elements=conflict_target, set_=obj)

            stmt = stmt.returning(self.model)
            result = _session.execute(stmt)
            _session.commit()
            logger.debug("Upsert operation successful on %s", self.model.__tablename__)

            return result.first()[0]
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to upsert data in %s: %s", self.model.__tablename__, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to upsert data in {self.model.__tablename__}") from e
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
    ) -> List[Provider]:
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
                obj: dict = data.copy() if isinstance(data, dict) else data.model_dump(exclude_unset=True)
            else:
                raise ValueError("Invalid data type for upsert")

            stmt = insert(self.model.__table__).values(obj)
            if conflict_target:
                stmt = stmt.on_conflict_do_update(index_elements=conflict_target, set_=obj)

            stmt = stmt.returning(self.model)
            result = _session.execute(stmt)
            _session.commit()
            logger.debug("Upsert operation successful on %s", self.model.__tablename__)

            return result.first()[0]
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to upsert data in %s: %s", self.model.__tablename__, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to upsert data in {self.model.__tablename__}") from e
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
