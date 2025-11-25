import logging
import re
from typing import Any, Dict, List, Optional
from uuid import UUID

from budmicroframe.commons.exceptions import ClientException
from sqlalchemy.orm import Session

from budconnect.engine.crud import (
    EngineCompatibilityCRUD,
    EngineCRUD,
    EngineToolParserRuleCRUD,
    EngineVersionCRUD,
)
from budconnect.engine.models import Engine, EngineCompatibility, EngineToolParserRule, EngineVersion
from budconnect.model.crud import ModelArchitectureClassCRUD, ModelInfoCRUD
from budconnect.model.models import engine_version_model_info, engine_version_provider

from .schemas import (
    DeviceArchitecture,
    EngineCompatibilityCreate,
    EngineCompatibilityUpdate,
    EngineCreate,
    EngineToolParserRuleCreate,
    EngineToolParserRuleUpdate,
    EngineUpdate,
    EngineVersionCreate,
    EngineVersionUpdate,
    LatestEngineVersion,
    ParserMatchType,
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
    ) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
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
            update_data["device_architecture"] = version_data.device_architecture.value
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
    def list_tool_parser_rules(
        engine_version_id: UUID, session: Optional[Session] = None
    ) -> List[EngineToolParserRule]:
        """List parser rules for an engine version ordered by priority."""
        with EngineToolParserRuleCRUD() as parser_rule_crud:
            rules, _ = parser_rule_crud.fetch_many(
                {"engine_version_id": engine_version_id},
                session=parser_rule_crud.session,
                order_by=[("priority", "asc")],
            )
            return rules or []

    @staticmethod
    def get_tool_parser_rule(rule_id: UUID, session: Optional[Session] = None) -> EngineToolParserRule:
        """Get a tool parser rule by ID."""
        rule = EngineToolParserRuleCRUD().fetch_one({"id": rule_id}, session=session)
        if not rule:
            raise ClientException(f"Parser rule with ID {rule_id} not found")
        return rule

    @staticmethod
    def create_tool_parser_rule(
        rule_data: EngineToolParserRuleCreate, session: Optional[Session] = None
    ) -> EngineToolParserRule:
        """Create a new tool parser rule for an engine version."""
        # Ensure referenced engine version exists
        EngineService.get_engine_version(rule_data.engine_version_id, session=session)
        logger.info(f"Before dump {rule_data}")
        try:
            payload = rule_data.model_dump()
            logger.info(f"Rule payload {payload}")
            # Convert enum to its value for database insertion
            if "match_type" in payload and hasattr(payload["match_type"], "value"):
                payload["match_type"] = payload["match_type"].value

            parser_type = payload.get("parser_type")
            if isinstance(parser_type, str):
                parser_type = parser_type.strip()
            payload["parser_type"] = parser_type or None

            chat_template = payload.get("chat_template")
            if isinstance(chat_template, str):
                chat_template = chat_template.strip()
            payload["chat_template"] = chat_template or None

            if not payload.get("parser_type") and not payload.get("chat_template"):
                raise ClientException("Either parser_type or chat_template must be provided")
            logger.info(f"Final Rule payload {payload}")
            return EngineToolParserRuleCRUD().insert(payload, session=session)
        except Exception as e:
            raise ClientException(f"Failed to create parser rule: {str(e)}") from e

    @staticmethod
    def update_tool_parser_rule(
        rule_id: UUID, rule_data: EngineToolParserRuleUpdate, session: Optional[Session] = None
    ) -> EngineToolParserRule:
        """Update an existing tool parser rule."""
        existing_rule = EngineService.get_tool_parser_rule(rule_id, session=session)

        update_payload = rule_data.model_dump(exclude_unset=True)
        if "parser_type" in update_payload:
            parser_type_value = update_payload.get("parser_type")
            if isinstance(parser_type_value, str):
                parser_type_value = parser_type_value.strip()
            update_payload["parser_type"] = parser_type_value or None
        if "chat_template" in update_payload:
            chat_template_value = update_payload.get("chat_template")
            if isinstance(chat_template_value, str):
                chat_template_value = chat_template_value.strip()
            update_payload["chat_template"] = chat_template_value or None
        if update_payload:
            if "match_type" in update_payload:
                match_type_value = update_payload.get("match_type")
                if isinstance(match_type_value, ParserMatchType):
                    update_payload["match_type"] = match_type_value.value
                else:
                    update_payload["match_type"] = ParserMatchType(match_type_value).value

            final_parser_type = (
                update_payload.get("parser_type") if "parser_type" in update_payload else existing_rule.parser_type
            )
            final_chat_template = (
                update_payload.get("chat_template")
                if "chat_template" in update_payload
                else existing_rule.chat_template
            )

            if not final_parser_type and not final_chat_template:
                raise ClientException("Either parser_type or chat_template must be provided")
            try:
                EngineToolParserRuleCRUD().update(update_payload, {"id": rule_id}, session=session)
            except Exception as e:
                raise ClientException(f"Failed to update parser rule: {str(e)}") from e

        return EngineService.get_tool_parser_rule(rule_id, session=session)

    @staticmethod
    def delete_tool_parser_rule(rule_id: UUID, session: Optional[Session] = None) -> bool:
        """Delete a tool parser rule."""
        EngineToolParserRuleCRUD().delete({"id": rule_id}, session=session)
        return True

    @staticmethod
    def get_compatible_engines(
        model_architecture: str,
        device_architecture: DeviceArchitecture,
        engine_version: str,
        engine: str,
        model_uri: Optional[str] = None,
    ) -> EngineCompatibility:
        """Check if a model architecture is compatible with a specific engine version and device architecture.

        This method returns a list of compatible engines for a given model architecture, device architecture, and engine version.

        Args:
            model_architecture (str): The architecture of the model to check.
            device_architecture (DeviceArchitecture): The architecture of the device.
            engine_version (str): The version of the engine.
            engine (str): The name of the engine.
            model_uri (Optional[str]): The model URI for precise capability lookup.

        Returns:
            Any: The compatibility information if compatible with tool calling and reasoning capabilities.

        Raises:
            ClientException: If the model architecture is not compatible.
        """
        # Initialize architecture info and model info
        architecture_info = None
        model_info = None

        # Try to get architecture info and model info from model URI first
        if model_uri:
            with ModelInfoCRUD() as model_crud:
                model_data = model_crud.get_by_uri_with_architecture(model_uri)
                if model_data:
                    if model_data[0]:  # ModelInfo exists
                        model_info = model_data[0]
                    if model_data[1]:  # ModelArchitectureClass exists
                        architecture_info = model_data[1]
                        logger.info(
                            f"Found architecture info for model URI {model_uri}: {architecture_info.class_name}"
                        )

        # Fallback to direct architecture lookup if not found via model URI
        if not architecture_info:
            with ModelArchitectureClassCRUD() as arch_crud:
                architecture_info = arch_crud.get_by_class_name(model_architecture)
                if architecture_info:
                    logger.info(f"Found architecture info for class {model_architecture}")

        # Get compatible engines
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

        parser_rules_by_version: Dict[UUID, List[EngineToolParserRule]] = {}
        if model_uri:
            version_ids = {
                engine_item.engine_version_id
                for engine_item in compatible_engines
                if engine_item.engine_version_id is not None
            }
            if version_ids:
                with EngineToolParserRuleCRUD() as parser_rule_crud:
                    parser_rules_by_version = parser_rule_crud.get_rules_for_versions(
                        list(version_ids), session=parser_rule_crud.session
                    )

        # Enhance response with architecture capabilities and chat template
        for engine_item in compatible_engines:
            matched_rule = None
            if model_uri and engine_item.engine_version_id:
                rules = parser_rules_by_version.get(engine_item.engine_version_id, [])
                matched_rule = EngineService._match_parser_rule(model_uri, rules)

            if model_info and model_info.tool_calling_parser_type:
                engine_item.tool_calling_parser_type = model_info.tool_calling_parser_type
                engine_item.parser_source = "model_default"

            if architecture_info:
                if not engine_item.tool_calling_parser_type and architecture_info.tool_calling_parser_type:
                    engine_item.tool_calling_parser_type = architecture_info.tool_calling_parser_type
                    engine_item.parser_source = engine_item.parser_source or "architecture_default"
                engine_item.reasoning_parser_type = architecture_info.reasoning_parser_type
                engine_item.architecture_family = architecture_info.architecture_family
                engine_item.supports_lora = architecture_info.supports_lora
                engine_item.supports_pipeline_parallelism = architecture_info.supports_pipeline_parallelism

            if matched_rule:
                if matched_rule.chat_template is not None:
                    engine_item.chat_template = matched_rule.chat_template
                if matched_rule.notes:
                    engine_item.parser_notes = matched_rule.notes
                if matched_rule.parser_type and not engine_item.tool_calling_parser_type:
                    engine_item.tool_calling_parser_type = matched_rule.parser_type
                    engine_item.parser_source = engine_item.parser_source or "engine_parser_rule"

            # Add chat_template if model_info is available
            if model_info and engine_item.chat_template is None:
                engine_item.chat_template = model_info.chat_template

        return compatible_engines

    @staticmethod
    def _match_parser_rule(model_identifier: str, rules: List[EngineToolParserRule]) -> Optional[EngineToolParserRule]:
        """Select the first enabled parser rule that matches the provided model identifier."""
        if not rules:
            return None

        # Ensure deterministic ordering if the caller did not pre-sort
        ordered_rules = sorted(
            rules,
            key=lambda r: (r.priority or 0, str(r.id)),
        )

        for rule in ordered_rules:
            if not rule.enabled:
                continue

            if rule.match_type == ParserMatchType.EXACT and model_identifier == rule.pattern:
                return rule

            if rule.match_type == ParserMatchType.PREFIX and model_identifier.startswith(rule.pattern):
                return rule

            if rule.match_type == ParserMatchType.REGEX:
                try:
                    if re.match(rule.pattern, model_identifier):
                        return rule
                except re.error as exc:
                    logger.warning("Invalid regex pattern for parser rule %s: %s", rule.id, exc)
                    continue

        return None

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
                compat_dict = {
                    "id": str(compatibility.id),
                    "engine_version_id": str(compatibility.engine_version_id),
                    "architectures": compatibility.architectures,
                    "features": compatibility.features,
                }
                # Add optional timestamp fields if they exist
                if hasattr(compatibility, "created_at") and compatibility.created_at:
                    compat_dict["created_at"] = str(compatibility.created_at)
                if hasattr(compatibility, "updated_at") and compatibility.updated_at:
                    compat_dict["updated_at"] = str(compatibility.updated_at)
                compatibilities.append(compat_dict)

            # Create a response object with all the data we need
            response = LatestEngineVersion(version=engine_version.version, compatibilities=compatibilities)

            return response
