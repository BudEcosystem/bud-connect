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

"""CRUD operations for A2A registry agents."""

from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.shared.psql_service import CRUDMixin
from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models import A2ARegistryAgent


logger = logging.get_logger(__name__)


class A2ARegistryAgentCRUD(CRUDMixin[A2ARegistryAgent, None, None]):
    """CRUD operations for A2A registry agents."""

    __model__ = A2ARegistryAgent

    def __init__(self) -> None:
        """Initialize the A2ARegistryAgentCRUD class."""
        super().__init__(self.__model__)

    def upsert_by_base_url(
        self,
        data: Dict[str, Any],
        session: Optional[Session] = None,
    ) -> UUID:
        """Insert or update an agent by base_url.

        Args:
            data: Agent data dict matching A2ARegistryAgentCreate fields.
            session: Existing SQLAlchemy session. If None, creates new one.

        Returns:
            UUID: The ID of the created or updated record.
        """
        _session = session or self.get_session()
        try:
            stmt = insert(self.__model__.__table__).values(data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["base_url"],
                set_={k: v for k, v in data.items() if k != "id"},
            )
            stmt = stmt.returning(self.__model__.id)
            result = _session.execute(stmt)
            row = result.first()
            if session is None:
                _session.commit()

            if row:
                return UUID(str(row[0]))

            raise ValueError("No result returned from upsert operation")
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to upsert A2A agent: %s", e)
            raise ValueError("Failed to upsert A2A agent") from e
        finally:
            self.cleanup_session(_session if session is None else None)

    def fetch_many(
        self,
        page: int = 1,
        page_size: int = 50,
        session: Optional[Session] = None,
    ) -> Tuple[int, List[A2ARegistryAgent]]:
        """Fetch paginated A2A registry agents.

        Args:
            page: Page number (1-indexed).
            page_size: Number of results per page.
            session: Existing SQLAlchemy session.

        Returns:
            Tuple of (total_count, list_of_agents).
        """
        _session = session or self.get_session()
        try:
            query = _session.query(self.__model__)

            total = query.count()
            offset = (page - 1) * page_size
            agents = query.order_by(self.__model__.name).offset(offset).limit(page_size).all()

            return total, agents
        finally:
            self.cleanup_session(_session if session is None else None)

    def delete_absent(
        self,
        current_base_urls: Set[str],
        session: Optional[Session] = None,
    ) -> int:
        """Hard-delete agents whose base_url is NOT in the given set.

        Args:
            current_base_urls: Set of base_urls from the latest registry fetch.
            session: Existing SQLAlchemy session.

        Returns:
            Number of deleted rows.
        """
        if not current_base_urls:
            return 0

        _session = session or self.get_session()
        try:
            stmt = delete(self.__model__).where(self.__model__.base_url.notin_(current_base_urls))
            result = _session.execute(stmt)
            deleted = result.rowcount
            if session is None:
                _session.commit()
            if deleted > 0:
                logger.info("Deleted %d absent A2A registry agents", deleted)
            return deleted
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception("Failed to delete absent A2A agents: %s", e)
            return 0
        finally:
            self.cleanup_session(_session if session is None else None)

    def count(self, session: Optional[Session] = None) -> int:
        """Count total active A2A registry agents.

        Args:
            session: Existing SQLAlchemy session.

        Returns:
            Total number of agents.
        """
        _session = session or self.get_session()
        try:
            return _session.query(func.count(self.__model__.id)).scalar() or 0
        finally:
            self.cleanup_session(_session if session is None else None)
