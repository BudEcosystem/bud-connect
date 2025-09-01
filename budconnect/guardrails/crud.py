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

"""CRUD operations for guardrail models."""

from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.shared.psql_service import CRUDMixin, DBCreateSchemaType, ModelType
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..model.models import Provider
from .models import GuardrailProbe, GuardrailRule


logger = logging.get_logger(__name__)


class GuardrailProbeCRUD(CRUDMixin[GuardrailProbe, None, None]):
    __model__ = GuardrailProbe

    def __init__(self) -> None:
        """Initialize the GuardrailProbeCRUD class.

        This constructor initializes the GuardrailProbeCRUD class by calling the parent
        CRUDMixin constructor with the GuardrailProbe model. The GuardrailProbeCRUD class provides
        database operations for the GuardrailProbe model.
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

    def get_compatible_providers(
        self, provider_id: UUID, offset: int, limit: int, session: Optional[Session] = None
    ) -> Tuple[int, List[GuardrailProbe]]:
        """Get the guardrail probes for a given provider.

        Args:
            provider_id: The ID of the provider to get guardrail probes for.
            offset: The offset to start the pagination from.
            limit: The number of probes to return.
            session: The session to use for the query.

        Returns:
            A tuple containing the total count and list of guardrail probes with rules count.
        """
        _session = session or self.get_session()
        try:
            # Get total count of probes for this provider
            total_probes = (
                _session.query(func.count(GuardrailProbe.id))
                .filter(GuardrailProbe.provider_id == provider_id)
                .scalar()
            )

            # Get probes with rules count
            query = (
                _session.query(GuardrailProbe, func.count(GuardrailRule.id).label("rules_count"))
                .outerjoin(GuardrailRule, GuardrailProbe.id == GuardrailRule.probe_id)
                .filter(GuardrailProbe.provider_id == provider_id)
                .group_by(GuardrailProbe.id)
                .order_by(GuardrailProbe.name)
                .offset(offset)
                .limit(limit)
            )

            results = query.all()

            # Process results to include rules count and hybrid properties
            probes_with_details = []
            for probe, rules_count in results:
                # Access hybrid properties to ensure they're loaded
                probe.rules_count = rules_count
                # The hybrid properties will be automatically included when serializing
                # They include: guard_types, scanner_types, modality_types, examples
                probes_with_details.append(probe)

            return total_probes, probes_with_details
        finally:
            self.cleanup_session(_session if session is None else None)

    def get_providers_with_guardrails(
        self, version_id: UUID, offset: int, limit: int, session: Optional[Session] = None
    ) -> Tuple[int, List[Provider]]:
        """Get providers that have guardrail probes and are compatible with the engine version.

        Args:
            version_id: The ID of the engine version to get compatible providers for.
            offset: The offset to start the pagination from.
            limit: The number of providers to return.
            session: The session to use for the query.

        Returns:
            A tuple of (total_count, list of providers with guardrails).
        """
        _session = session or self.get_session()
        try:
            from ..model.models import engine_version_provider

            # Base query for providers with guardrails that are compatible with the engine version
            base_query = (
                _session.query(Provider)
                .join(GuardrailProbe, GuardrailProbe.provider_id == Provider.id)
                .join(engine_version_provider, Provider.id == engine_version_provider.c.provider_id)
                .filter(engine_version_provider.c.engine_version_id == version_id)
                .distinct()
            )

            # Get total count
            total_count = base_query.count()

            # Get paginated results
            providers = base_query.order_by(Provider.name).offset(offset).limit(limit).all()

            return total_count, providers
        finally:
            self.cleanup_session(_session if session is None else None)


class GuardrailRuleCRUD(CRUDMixin[GuardrailRule, None, None]):
    __model__ = GuardrailRule

    def __init__(self) -> None:
        """Initialize the GuardrailRuleCRUD class.

        This constructor initializes the GuardrailRuleCRUD class by calling the parent
        CRUDMixin constructor with the GuardrailRule model. The GuardrailRuleCRUD class provides
        database operations for the GuardrailRule model.
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

    def get_by_probe_id(
        self, probe_id: UUID, offset: int, limit: int, session: Optional[Session] = None
    ) -> Optional[Dict[str, Any]]:
        """Get guardrail probe details with paginated rules and provider information.

        Args:
            probe_id: The ID of the probe to get details for.
            offset: The offset to start the pagination from for rules.
            limit: The number of rules to return.
            session: The session to use for the query.

        Returns:
            A dictionary containing probe details, provider info, and paginated rules if found, None otherwise.
        """
        _session = session or self.get_session()
        try:
            # First, get the probe with provider information
            probe_result = (
                _session.query(
                    GuardrailProbe,
                    Provider.id.label("provider_id"),
                    Provider.name.label("provider_name"),
                    Provider.provider_type.label("provider_type"),
                    Provider.icon.label("provider_icon"),
                    Provider.description.label("provider_description"),
                )
                .join(Provider, GuardrailProbe.provider_id == Provider.id)
                .filter(GuardrailProbe.id == probe_id)
                .first()
            )

            if not probe_result:
                return None

            probe, provider_id, provider_name, provider_type, provider_icon, provider_description = probe_result

            # Get total count of rules for this probe
            total_rules = (
                _session.query(func.count(GuardrailRule.id)).filter(GuardrailRule.probe_id == probe_id).scalar()
            )

            # Get paginated rules
            rules_query = (
                _session.query(GuardrailRule)
                .filter(GuardrailRule.probe_id == probe_id)
                .order_by(GuardrailRule.name)
                .offset(offset)
                .limit(limit)
            )

            rules = rules_query.all()

            # Combine all data into a single dictionary
            combined_data = {
                # Probe fields
                "id": probe.id,
                "uri": probe.uri,
                "name": probe.name,
                "description": probe.description,
                "tags": probe.tags,
                "examples": probe.examples,  # This will use the hybrid property
                "deprecation_date": probe.deprecation_date,
                "guard_types": probe.guard_types,  # Hybrid property
                "scanner_types": probe.scanner_types,  # Hybrid property
                "modality_types": probe.modality_types,  # Hybrid property
                "created_at": probe.created_at,
                "modified_at": probe.modified_at,
                # Provider fields
                "provider_id": provider_id,
                "provider_name": provider_name,
                "provider_type": provider_type,
                "provider_icon": provider_icon,
                "provider_description": provider_description,
                # Rules pagination info
                "total_items": total_rules,
                # Rules data
                "items": [
                    {
                        "id": rule.id,
                        "uri": rule.uri,
                        "name": rule.name,
                        "description": rule.description,
                        "examples": rule.examples,
                        "deprecation_date": rule.deprecation_date,
                        "guard_types": rule.guard_types,
                        "scanner_types": rule.scanner_types,
                        "modality_types": rule.modality_types,
                        "created_at": rule.created_at,
                        "modified_at": rule.modified_at,
                    }
                    for rule in rules
                ],
            }

            return combined_data
        finally:
            self.cleanup_session(_session if session is None else None)
