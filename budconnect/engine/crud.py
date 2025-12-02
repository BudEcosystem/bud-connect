import logging
from typing import Dict, List, Optional
from uuid import UUID

from budmicroframe.shared.psql_service import CRUDMixin
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .models import Engine, EngineCompatibility, EngineToolParserRule, EngineVersion
from .schemas import CompatibleEngine, DeviceArchitecture


logger = logging.getLogger(__name__)


class EngineCRUD(CRUDMixin[Engine, None, None]):
    __model__ = Engine

    def __init__(self) -> None:
        """Initialize the EngineCRUD class.

        This constructor initializes the EngineCRUD class by calling the parent
        CRUDMixin constructor with the Engine model. The EngineCRUD class provides
        database operations for the Engine model.
        """
        super().__init__(self.__model__)

    def get_latest_engine_version(
        self, device_architecture: DeviceArchitecture, engine: str, session: Optional[Session] = None
    ) -> Optional[EngineVersion]:
        """Get the latest version of a specific engine for a given device architecture.

        This method retrieves the most recent version of the specified engine that is compatible
        with the provided device architecture. It first finds the engine by name, then queries
        for the latest version based on creation timestamp.

        Args:
            device_architecture (DeviceArchitecture): The architecture of the device.
            engine (str): The name of the engine to query.
            session (Optional[Session], optional): SQLAlchemy session to use. If None, a new session will be created.

        Returns:
            Optional[EngineVersion]: The latest engine version object if found, None otherwise.
        """
        session = session or self.get_session()

        # First, find the engine by name
        engine_obj = session.query(Engine).filter(Engine.name == engine).first()

        if not engine_obj:
            return None

        # Then, find the latest version for this engine and device architecture
        engine_version: Optional[EngineVersion] = (
            session.query(EngineVersion)
            .filter(EngineVersion.device_architecture == device_architecture, EngineVersion.engine_id == engine_obj.id)
            .order_by(EngineVersion.created_at.desc())
            .first()
        )

        return engine_version

    def get_compatible_engines(
        self,
        model_architecture: str,
        device_architecture: Optional[DeviceArchitecture] = None,
        engine_version: Optional[str] = None,
        engine: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> List[CompatibleEngine]:
        """Get compatible engines for a given model architecture, device architecture, and engine version.

        This method retrieves compatible engines for a given model architecture, device architecture, and engine version.
        It performs a database query with joins to efficiently retrieve the compatibility information.

        If engine, engine_version, or device_architecture are not provided, the method will find the latest
        compatible version for each engine and device architecture combination.

        Args:
            model_architecture (str): The architecture of the model to validate.
            device_architecture (Optional[DeviceArchitecture], optional): The architecture of the device. If None, all architectures are considered.
            engine_version (Optional[str], optional): The version of the engine. If None, the latest version for each engine will be used.
            engine (Optional[str], optional): The name of the engine. If None, all engines are considered.
            session (Optional[Session], optional): SQLAlchemy session to use. If None, a new session will be created.

        Returns:
            list[dict]: A list of dictionaries containing engine name, device architecture, and version for compatible combinations.
        """
        session = session or self.get_session()

        # Build base query with the columns we need
        query = (
            session.query(
                Engine.name.label("engine"),
                EngineVersion.id.label("engine_version_id"),
                EngineVersion.device_architecture.label("device_architecture"),
                EngineVersion.version.label("version"),
                EngineVersion.engine_id.label("engine_id"),
                EngineVersion.container_image.label("container_image"),
            )
            .select_from(EngineCompatibility)
            .join(EngineVersion, EngineCompatibility.engine_version_id == EngineVersion.id)
            .join(Engine, EngineVersion.engine_id == Engine.id)
            .filter(
                func.jsonb_extract_path_text(EngineCompatibility.architectures, "architectures").like(
                    f'%"{model_architecture}"%'
                )
            )
        )

        # Apply optional filters
        if engine:
            query = query.filter(Engine.name == engine)

        if engine_version:
            query = query.filter(EngineVersion.version == engine_version)

        if device_architecture:
            query = query.filter(EngineVersion.device_architecture == device_architecture)

        # If no specific version is requested, get the latest for each engine/device combination
        if not engine_version:
            # Use a window function to rank versions by creation date for each engine/device combination
            latest_versions = session.query(
                EngineVersion.id,
                func.row_number()
                .over(
                    partition_by=[EngineVersion.engine_id, EngineVersion.device_architecture],
                    order_by=EngineVersion.created_at.desc(),
                )
                .label("rn"),
            ).subquery()

            # Only include the top-ranked version for each combination
            query = query.join(
                latest_versions, (EngineVersion.id == latest_versions.c.id) & (latest_versions.c.rn == 1)
            )

        # Execute query and convert results to dictionaries
        results = query.all()
        compatible_engines = []
        for row in results:
            compatible_engines.append(
                CompatibleEngine(
                    engine=row.engine,
                    device_architecture=row.device_architecture,
                    version=row.version,
                    container_image=row.container_image,
                    engine_version_id=row.engine_version_id,
                    engine_id=row.engine_id,
                )
            )
        return compatible_engines


class EngineToolParserRuleCRUD(CRUDMixin[EngineToolParserRule, None, None]):
    __model__ = EngineToolParserRule

    def __init__(self) -> None:
        """Initialize the EngineToolParserRuleCRUD class."""
        super().__init__(self.__model__)

    def get_rules_for_engines(
        self,
        engine_ids: List[UUID],
        session: Optional[Session] = None,
    ) -> Dict[UUID, List[EngineToolParserRule]]:
        """Get parser rules for multiple engines grouped by engine ID."""
        if not engine_ids:
            return {}

        _session = session or self.get_session()
        try:
            query = (
                _session.query(EngineToolParserRule)
                .filter(EngineToolParserRule.engine_id.in_(engine_ids))
                .order_by(EngineToolParserRule.engine_id, EngineToolParserRule.priority.asc())
            )
            results = query.all()

            grouped: Dict[UUID, List[EngineToolParserRule]] = {}
            for rule in results:
                grouped.setdefault(rule.engine_id, []).append(rule)
            return grouped
        finally:
            if session is None:
                self.cleanup_session(_session)


class EngineVersionCRUD(CRUDMixin[EngineVersion, None, None]):
    """CRUD operations for EngineVersion model.

    This class provides create, read, update, and delete operations for the EngineVersion model,
    which represents different versions of engines with their specific device architectures and
    container images.
    """

    __model__ = EngineVersion

    def __init__(self) -> None:
        """Initialize the EngineVersionCRUD class.

        This constructor initializes the EngineVersionCRUD class by calling the parent
        CRUDMixin constructor with the EngineVersion model.
        """
        super().__init__(self.__model__)

    def get_latest_engine_version(
        self, engine_id: UUID, session: Optional[Session] = None, raise_on_error: bool = True
    ) -> Optional[EngineVersion]:
        """Get the latest engine version for a given engine.

        This method retrieves the latest engine version for a given engine. It first finds the engine by name, then queries
        for the latest version based on creation timestamp.

        Args:
            engine_id (UUID): The ID of the engine to get the latest version for.
            session (Optional[Session], optional): SQLAlchemy session to use. If None, a new session will be created.
            raise_on_error (bool, optional): Whether to raise an error if the latest engine version is not found. Defaults to True.

        Returns:
            Optional[EngineVersion]: The latest engine version object if found, None otherwise.
        """
        _session = session or self.get_session()

        try:
            stmt = (
                select(EngineVersion)
                .where(EngineVersion.engine_id == engine_id)
                .order_by(EngineVersion.created_at.desc())
            )
            result = _session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            _session.rollback()
            logger.exception(f"Error getting latest engine version for {engine_id}: {e}")
            if raise_on_error:
                raise e
            return None
        finally:
            self.cleanup_session(_session if session is None else None)


class EngineCompatibilityCRUD(CRUDMixin[EngineCompatibility, None, None]):
    """CRUD operations for EngineCompatibility model.

    This class provides create, read, update, and delete operations for the EngineCompatibility model,
    which defines the compatibility between engine versions and different architectures and features.
    It helps determine if a specific model architecture can run on a particular engine version and
    device architecture combination.
    """

    __model__ = EngineCompatibility

    def __init__(self) -> None:
        """Initialize the EngineCompatibilityCRUD class.

        This constructor initializes the EngineCompatibilityCRUD class by calling the parent
        CRUDMixin constructor with the EngineCompatibility model.
        """
        super().__init__(self.__model__)
