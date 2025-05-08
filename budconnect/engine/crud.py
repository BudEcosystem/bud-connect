import logging
from typing import Optional

from budmicroframe.shared.psql_service import CRUDMixin
from sqlalchemy.orm import Session

from .models import Engine, EngineCompatibility, EngineVersion
from .schemas import DeviceArchitecture


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

    def validate_model_compatibility(
        self,
        model_architecture: str,
        device_architecture: DeviceArchitecture,
        engine_version: str,
        engine: str,
        session: Optional[Session] = None,
    ) -> Optional[EngineCompatibility]:
        """Validate if a model architecture is compatible with a specific engine version and device architecture.

        This method checks if the provided model architecture is compatible with the specified engine version
        running on the given device architecture. It performs a database query with joins to efficiently
        retrieve the compatibility information.

        Args:
            model_architecture (str): The architecture of the model to validate.
            device_architecture (DeviceArchitecture): The architecture of the device.
            engine_version (str): The version of the engine.
            engine (str): The name of the engine.
            session (Optional[Session], optional): SQLAlchemy session to use. If None, a new session will be created.

        Returns:
            Optional[EngineCompatibility]: The compatibility object if the model is compatible, None otherwise.
        """
        session = session or self.get_session()

        # Use a single query with joins to get everything we need
        compatibility: Optional[EngineCompatibility] = (
            session.query(EngineCompatibility)
            .join(EngineVersion, EngineCompatibility.engine_version_id == EngineVersion.id)
            .join(Engine, EngineVersion.engine_id == Engine.id)
            .filter(
                Engine.name == engine,
                EngineVersion.version == engine_version,
                EngineVersion.device_architecture == device_architecture,
                # Use PostgreSQL's @> operator to check if the array contains an object with the specified name
                EngineCompatibility.architectures.contains([{"name": model_architecture}]),
            )
            .first()
        )

        return compatibility


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
