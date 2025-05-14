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

from typing import Dict, List, Optional, Union

from budmicroframe.commons import logging
from budmicroframe.shared.psql_service import CRUDMixin, DBCreateSchemaType, ModelType
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models import Provider


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
        data: Union[DBCreateSchemaType, ModelType, Dict],
        conflict_target: Optional[List[str]] = None,
        session: Optional[Session] = None,
        raise_on_error: bool = True,
    ):
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
            _session.execute(stmt)
            _session.commit()
            logger.debug("Upsert operation successful on %s", self.model.__tablename__)
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to upsert data in %s: %s", self.model.__tablename__, str(e))
            if raise_on_error:
                raise ValueError(f"Failed to upsert data in {self.model.__tablename__}") from e
        finally:
            self.cleanup_session(_session if session is None else None)
