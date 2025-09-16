import logging
from typing import Optional
from uuid import UUID

from budmicroframe.commons.exceptions import ClientException
from sqlalchemy.orm import Session

from budconnect.engine.crud import EngineCompatibilityCRUD, EngineCRUD, EngineVersionCRUD
from budconnect.engine.models import Engine, EngineCompatibility, EngineVersion
from budconnect.model.models import engine_version_model_info, engine_version_provider

from .schemas import (
    DeviceArchitecture,
    EngineCompatibilityCreate,
    EngineCompatibilityUpdate,
    EngineCreate,
    EngineUpdate,
    EngineVersionCreate,
    EngineVersionUpdate,
    LatestEngineVersion,
)
from .schemas import (
    Engine as EngineSchema,
)
from .schemas import (
    EngineVersion as EngineVersionSchema,
)


logger = logging.getLogger(__name__)


class EngineService:
    engine_crud = EngineCRUD()
    engine_version_crud = EngineVersionCRUD()
    engine_compatibility_crud = EngineCompatibilityCRUD()

    @staticmethod
    def create_engine(engine_data: EngineCreate, session: Optional[Session] = None) -> Engine:
        """Create a new engine."""
        try:
            engine = Engine(name=engine_data.name)
            return EngineService.engine_crud.insert(engine, session=session)
        except Exception as e:
            raise ClientException(f"Failed to create engine: {str(e)}") from e

    @staticmethod
    def get_engine(engine_id: UUID, session: Optional[Session] = None) -> Engine:
        """Get an engine by ID."""
        engine = EngineService.engine_crud.fetch_one(conditions={"id": engine_id}, session=session)
        if not engine:
            raise ClientException(f"Engine with ID {engine_id} not found")
        return engine

    @staticmethod
    def get_engines(
        page: int = 1, page_size: int = 20, search: Optional[str] = None, session: Optional[Session] = None
    ) -> dict:
        """Get all engines with pagination."""
        session = session or EngineService.engine_crud.get_session()
        query = session.query(Engine)

        if search:
            query = query.filter(Engine.name.ilike(f"%{search}%"))

        total = query.count()
        engines = query.offset((page - 1) * page_size).limit(page_size).all()

        # Convert SQLAlchemy models to Pydantic models
        engine_schemas = [
            EngineSchema(
                id=engine.id,
                name=engine.name,
                created_at=str(engine.created_at) if hasattr(engine, "created_at") and engine.created_at else None,
                updated_at=str(engine.updated_at) if hasattr(engine, "updated_at") and engine.updated_at else None,
            )
            for engine in engines
        ]

        return {"engines": engine_schemas, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def update_engine(engine_id: UUID, engine_data: EngineUpdate, session: Optional[Session] = None) -> Engine:
        """Update an engine."""
        EngineService.get_engine(engine_id, session=session)

        update_data = {}
        if engine_data.name is not None:
            update_data["name"] = engine_data.name

        if update_data:
            EngineService.engine_crud.update(data=update_data, conditions={"id": engine_id}, session=session)

        return EngineService.get_engine(engine_id, session=session)

    @staticmethod
    def delete_engine(engine_id: UUID, session: Optional[Session] = None) -> bool:
        """Delete an engine and all its versions."""
        engine = EngineService.get_engine(engine_id, session=session)

        # First delete all versions associated with this engine
        _session = session or EngineService.engine_crud.get_session()
        try:
            # Get all engine versions for this engine
            versions = _session.query(EngineVersion).filter(EngineVersion.engine_id == engine_id).all()

            for version in versions:
                # Delete all relationships for each version
                # Delete from engine_version_model_info association table
                _session.execute(
                    engine_version_model_info.delete().where(
                        engine_version_model_info.c.engine_version_id == version.id
                    )
                )

                # Delete from engine_version_provider association table
                _session.execute(
                    engine_version_provider.delete().where(engine_version_provider.c.engine_version_id == version.id)
                )

                # Delete compatibilities for each version
                _session.query(EngineCompatibility).filter(
                    EngineCompatibility.engine_version_id == version.id
                ).delete()

            # Now delete all versions
            _session.query(EngineVersion).filter(EngineVersion.engine_id == engine_id).delete()

            # Finally delete the engine itself
            EngineService.engine_crud.delete(conditions={"id": engine.id}, session=_session)

            if session is None:
                _session.commit()

            return True
        except Exception as e:
            if session is None:
                _session.rollback()
            raise ClientException(f"Failed to delete engine: {str(e)}") from e
        finally:
            if session is None:
                EngineService.engine_crud.cleanup_session(_session)

    @staticmethod
    def create_engine_version(version_data: EngineVersionCreate, session: Optional[Session] = None) -> EngineVersion:
        """Create a new engine version."""
        try:
            # Verify engine exists
            EngineService.get_engine(version_data.engine_id, session=session)

            version = EngineVersion(
                engine_id=version_data.engine_id,
                version=version_data.version,
                device_architecture=version_data.device_architecture,
                container_image=version_data.container_image,
            )
            return EngineService.engine_version_crud.insert(version, session=session)
        except Exception as e:
            raise ClientException(f"Failed to create engine version: {str(e)}") from e

    @staticmethod
    def get_engine_version(version_id: UUID, session: Optional[Session] = None) -> EngineVersion:
        """Get an engine version by ID."""
        version = EngineService.engine_version_crud.fetch_one(conditions={"id": version_id}, session=session)
        if not version:
            raise ClientException(f"Engine version with ID {version_id} not found")
        return version

    @staticmethod
    def get_engine_versions(
        engine_id: Optional[UUID] = None, page: int = 1, page_size: int = 20, session: Optional[Session] = None
    ) -> dict:
        """Get engine versions with pagination."""
        session = session or EngineService.engine_version_crud.get_session()
        query = session.query(EngineVersion)

        if engine_id:
            query = query.filter(EngineVersion.engine_id == engine_id)

        total = query.count()
        versions = query.offset((page - 1) * page_size).limit(page_size).all()

        # Convert SQLAlchemy models to Pydantic models
        version_schemas = [
            EngineVersionSchema(
                id=version.id,
                version=version.version,
                device_architecture=version.device_architecture,
                container_image=version.container_image,
                engine_id=version.engine_id,
                created_at=str(version.created_at) if hasattr(version, "created_at") and version.created_at else None,
                updated_at=str(version.updated_at) if hasattr(version, "updated_at") and version.updated_at else None,
            )
            for version in versions
        ]

        return {"versions": version_schemas, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def update_engine_version(
        version_id: UUID, version_data: EngineVersionUpdate, session: Optional[Session] = None
    ) -> EngineVersion:
        """Update an engine version."""
        EngineService.get_engine_version(version_id, session=session)

        update_data = {}
        if version_data.version is not None:
            update_data["version"] = version_data.version
        if version_data.device_architecture is not None:
            update_data["device_architecture"] = version_data.device_architecture
        if version_data.container_image is not None:
            update_data["container_image"] = version_data.container_image

        if update_data:
            EngineService.engine_version_crud.update(data=update_data, conditions={"id": version_id}, session=session)

        return EngineService.get_engine_version(version_id, session=session)

    @staticmethod
    def delete_engine_version(version_id: UUID, session: Optional[Session] = None) -> bool:
        """Delete an engine version and all its relationships."""
        version = EngineService.get_engine_version(version_id, session=session)

        _session = session or EngineService.engine_version_crud.get_session()
        try:
            # Delete from association tables first
            # Delete from engine_version_model_info association table
            _session.execute(
                engine_version_model_info.delete().where(engine_version_model_info.c.engine_version_id == version_id)
            )

            # Delete from engine_version_provider association table
            _session.execute(
                engine_version_provider.delete().where(engine_version_provider.c.engine_version_id == version_id)
            )

            # Delete compatibilities
            _session.query(EngineCompatibility).filter(EngineCompatibility.engine_version_id == version_id).delete()

            # Now delete the version itself
            EngineService.engine_version_crud.delete(conditions={"id": version.id}, session=_session)

            if session is None:
                _session.commit()

            return True
        except Exception as e:
            if session is None:
                _session.rollback()
            raise ClientException(f"Failed to delete engine version: {str(e)}") from e
        finally:
            if session is None:
                EngineService.engine_version_crud.cleanup_session(_session)

    @staticmethod
    def create_engine_compatibility(
        compatibility_data: EngineCompatibilityCreate, session: Optional[Session] = None
    ) -> EngineCompatibility:
        """Create a new engine compatibility."""
        try:
            # Verify engine version exists
            EngineService.get_engine_version(compatibility_data.engine_version_id, session=session)

            compatibility = EngineCompatibility(
                engine_version_id=compatibility_data.engine_version_id,
                architectures=compatibility_data.architectures,
                features=compatibility_data.features,
            )
            return EngineService.engine_compatibility_crud.insert(compatibility, session=session)
        except Exception as e:
            raise ClientException(f"Failed to create engine compatibility: {str(e)}") from e

    @staticmethod
    def update_engine_compatibility(
        compatibility_id: UUID, compatibility_data: EngineCompatibilityUpdate, session: Optional[Session] = None
    ) -> EngineCompatibility:
        """Update an engine compatibility."""
        session = session or EngineService.engine_compatibility_crud.get_session()
        compatibility = session.query(EngineCompatibility).filter(EngineCompatibility.id == compatibility_id).first()

        if not compatibility:
            raise ClientException(f"Engine compatibility with ID {compatibility_id} not found")

        update_data = {}
        if compatibility_data.architectures is not None:
            update_data["architectures"] = compatibility_data.architectures
        if compatibility_data.features is not None:
            update_data["features"] = compatibility_data.features

        if update_data:
            EngineService.engine_compatibility_crud.update(
                data=update_data, conditions={"id": compatibility_id}, session=session
            )

        return session.query(EngineCompatibility).filter(EngineCompatibility.id == compatibility_id).first()

    @staticmethod
    def delete_engine_compatibility(compatibility_id: UUID, session: Optional[Session] = None) -> bool:
        """Delete an engine compatibility."""
        session = session or EngineService.engine_compatibility_crud.get_session()
        compatibility = session.query(EngineCompatibility).filter(EngineCompatibility.id == compatibility_id).first()

        if not compatibility:
            raise ClientException(f"Engine compatibility with ID {compatibility_id} not found")

        EngineService.engine_compatibility_crud.delete(conditions={"id": compatibility.id}, session=session)
        return True

    @staticmethod
    def get_compatible_engines(
        model_architecture: str, device_architecture: DeviceArchitecture, engine_version: str, engine: str
    ) -> EngineCompatibility:
        """Check if a model architecture is compatible with a specific engine version and device architecture.

        This method returns a list of compatible engines for a given model architecture, device architecture, and engine version.

        Args:
            model_architecture (str): The architecture of the model to check.
            device_architecture (DeviceArchitecture): The architecture of the device.
            engine_version (str): The version of the engine.
            engine (str): The name of the engine.

        Returns:
            Any: The compatibility information if compatible.

        Raises:
            ClientException: If the model architecture is not compatible.
        """
        with EngineCRUD() as engine_crud:
            logger.info(
                f"Checking model compatibility for {model_architecture} on {device_architecture} with {engine} version {engine_version}"
            )
            compatible_engines = engine_crud.get_compatible_engines(
                model_architecture, device_architecture, engine_version, engine
            )

            logger.info(f"Compatible engines: {compatible_engines}")

        if not compatible_engines:
            raise ClientException(
                message="Model architecture is not compatible with the given device architecture and engine version"
            )
        return compatible_engines  # type: ignore

    @staticmethod
    def get_latest_engine_version(
        device_architecture: DeviceArchitecture, engine: str = "vllm"
    ) -> LatestEngineVersion:
        """Get the latest engine version for a device architecture."""
        with EngineCRUD() as engine_crud:
            # Use the session to query for the engine version
            engine_version = engine_crud.get_latest_engine_version(
                device_architecture=device_architecture, engine=engine
            )

            if not engine_version:
                raise ClientException(f"No engine version found for {device_architecture}")

            logger.info(f"Latest engine version for {device_architecture}: {engine_version}")

            # Explicitly load the compatibilities relationship before the session closes
            compatibilities = []
            for compatibility in engine_version.compatibilities:
                compatibilities.append(
                    {
                        "engine_version_id": str(compatibility.engine_version_id),
                        "architectures": compatibility.architectures,
                        "features": compatibility.features,
                    }
                )

            # Create a response object with all the data we need
            response = LatestEngineVersion(version=engine_version.version, compatibilities=compatibilities)

            return response
