import logging

from budmicroframe.commons.exceptions import ClientException

from budconnect.engine.crud import EngineCRUD

from .schemas import DeviceArchitecture, EngineCompatibility, LatestEngineVersion


logger = logging.getLogger(__name__)


class EngineService:
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
