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

from typing import Optional, Union
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from budmicroframe.commons.schemas import ErrorResponse
from fastapi import APIRouter, Query, status

from . import models, schemas
from .schemas import (
    CompatibleEnginesResponse,
    DeviceArchitecture,
    EngineCompatibilityCreate,
    EngineCompatibilityResponse,
    EngineCompatibilityUpdate,
    EngineCreate,
    EngineListResponse,
    EngineParserRuleCreate,
    EngineParserRuleListResponse,
    EngineParserRuleResponse,
    EngineParserRuleUpdate,
    EngineResponse,
    EngineUpdate,
    EngineVersionCreate,
    EngineVersionListResponse,
    EngineVersionResponse,
    EngineVersionUpdate,
    LatestEngineVersionResponse,
    ParserRuleType,
)
from .services import EngineService


logger = logging.get_logger(__name__)

engine_router = APIRouter(prefix="/engine", tags=["Engine"])


def _build_parser_rule_schema(rule: models.EngineParserRule) -> schemas.EngineParserRule:
    return schemas.EngineParserRule(
        id=rule.id,
        engine_id=rule.engine_id,
        rule_type=rule.rule_type,
        parser_type=rule.parser_type,
        match_type=rule.match_type,
        pattern=rule.pattern,
        priority=rule.priority,
        enabled=rule.enabled,
        notes=rule.notes,
        chat_template=rule.chat_template,
        created_at=str(rule.created_at) if hasattr(rule, "created_at") and rule.created_at else None,
        modified_at=str(rule.modified_at) if hasattr(rule, "modified_at") and rule.modified_at else None,
    )


# Engine CRUD endpoints
@engine_router.post("/")
async def create_engine(engine_data: EngineCreate) -> Union[EngineResponse, ErrorResponse]:
    """Create a new engine."""
    try:
        engine = EngineService.create_engine(engine_data)
        engine_schema = schemas.Engine(
            id=engine.id,
            name=engine.name,
            created_at=str(engine.created_at) if hasattr(engine, "created_at") and engine.created_at else None,
            updated_at=str(engine.updated_at) if hasattr(engine, "updated_at") and engine.updated_at else None,
        )
        response = EngineResponse(
            message="Engine created successfully",
            code=status.HTTP_201_CREATED,
            object="engine",
            engine=engine_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating engine: {e}")
        response = ErrorResponse(message="Error creating engine", code=500)
    return response.to_http_response()


@engine_router.get("/")
async def get_engines(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
) -> Union[EngineListResponse, ErrorResponse]:
    """Get all engines with pagination."""
    try:
        result = EngineService.get_engines(page=page, page_size=page_size, search=search)
        response = EngineListResponse(
            message="Engines retrieved successfully",
            code=status.HTTP_200_OK,
            object="engine.list",
            **result,
        )
    except Exception as e:
        logger.error(f"Error retrieving engines: {e}")
        response = ErrorResponse(message="Error retrieving engines", code=500)
    return response.to_http_response()


# IMPORTANT: Specific routes MUST come before parameterized routes
@engine_router.get("/get-compatible-engines")
async def get_compatible_engines(
    model_architecture: str,
    device_architecture: Union[DeviceArchitecture, None] = None,
    engine_version: Union[str, None] = None,
    engine: Union[str, None] = None,
    model_uri: Union[str, None] = None,
) -> Union[CompatibleEnginesResponse, ErrorResponse]:
    """Check if a model architecture is compatible with a device architecture and engine version.

    Args:
        model_architecture: The architecture of the model to check compatibility for
        device_architecture: The architecture of the device (CUDA, ROCM, CPU, HPU)
        engine_version: The version of the engine to check compatibility against
        engine: The engine name (e.g., "vllm")
        model_uri: Optional model URI for precise capability lookup (e.g., "meta-llama/Llama-3.2-1B")

    Returns:
        HTTP response with compatibility check results including tool calling and reasoning capabilities
    """
    try:
        # Cast Optional types to their required types as expected by the service
        compatible_engines = EngineService.get_compatible_engines(
            model_architecture=model_architecture,
            device_architecture=device_architecture,  # type: ignore
            engine_version=engine_version,  # type: ignore
            engine=engine,  # type: ignore
            model_uri=model_uri,  # Pass new parameter
        )
        response = CompatibleEnginesResponse(
            message="Model architecture is compatible with the given device architecture and engine version",
            code=status.HTTP_200_OK,
            object="engine.compatibility",
            compatible_engines=compatible_engines,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error checking model compatibility: {e}")
        response = ErrorResponse(message="Error checking model compatibility", code=500)

    return response.to_http_response()


@engine_router.get("/get-latest-engine-version")
async def get_latest_engine_version(
    device_architecture: DeviceArchitecture, engine: str
) -> Union[LatestEngineVersionResponse, ErrorResponse]:
    """Get the latest engine version for a device architecture."""
    try:
        latest_engine = EngineService.get_latest_engine_version(device_architecture, engine)

        response = LatestEngineVersionResponse(
            version=latest_engine.version,
            compatibilities=latest_engine.compatibilities,
            message="Engine version fetched successfully",
            code=status.HTTP_200_OK,
            object="engine.version",
        )
    except ClientException as e:
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error getting latest engine version: {e}")
        response = ErrorResponse(message="Error getting latest engine version", code=500)
    return response.to_http_response()


# Parameterized routes come AFTER specific routes
@engine_router.get("/{engine_id}")
async def get_engine(engine_id: UUID) -> Union[EngineResponse, ErrorResponse]:
    """Get an engine by ID."""
    try:
        engine = EngineService.get_engine(engine_id)
        engine_schema = schemas.Engine(
            id=engine.id,
            name=engine.name,
            created_at=str(engine.created_at) if hasattr(engine, "created_at") and engine.created_at else None,
            updated_at=str(engine.updated_at) if hasattr(engine, "updated_at") and engine.updated_at else None,
        )
        response = EngineResponse(
            message="Engine retrieved successfully",
            code=status.HTTP_200_OK,
            object="engine",
            engine=engine_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving engine: {e}")
        response = ErrorResponse(message="Error retrieving engine", code=500)
    return response.to_http_response()


@engine_router.put("/{engine_id}")
async def update_engine(engine_id: UUID, engine_data: EngineUpdate) -> Union[EngineResponse, ErrorResponse]:
    """Update an engine."""
    try:
        engine = EngineService.update_engine(engine_id, engine_data)
        engine_schema = schemas.Engine(
            id=engine.id,
            name=engine.name,
            created_at=str(engine.created_at) if hasattr(engine, "created_at") and engine.created_at else None,
            updated_at=str(engine.updated_at) if hasattr(engine, "updated_at") and engine.updated_at else None,
        )
        response = EngineResponse(
            message="Engine updated successfully",
            code=status.HTTP_200_OK,
            object="engine",
            engine=engine_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating engine: {e}")
        response = ErrorResponse(message="Error updating engine", code=500)
    return response.to_http_response()


@engine_router.delete("/{engine_id}")
async def delete_engine(engine_id: UUID) -> Union[EngineResponse, ErrorResponse]:
    """Delete an engine."""
    try:
        EngineService.delete_engine(engine_id)
        response = EngineResponse(
            message="Engine deleted successfully",
            code=status.HTTP_200_OK,
            object="engine",
            engine=None,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting engine: {e}")
        response = ErrorResponse(message="Error deleting engine", code=500)
    return response.to_http_response()


# Engine Version CRUD endpoints
@engine_router.post("/version/")
async def create_engine_version(version_data: EngineVersionCreate) -> Union[EngineVersionResponse, ErrorResponse]:
    """Create a new engine version."""
    try:
        version = EngineService.create_engine_version(version_data)
        version_schema = schemas.EngineVersion(
            id=version.id,
            version=version.version,
            device_architecture=version.device_architecture,
            container_image=version.container_image,
            engine_id=version.engine_id,
            created_at=str(version.created_at) if hasattr(version, "created_at") and version.created_at else None,
            updated_at=str(version.updated_at) if hasattr(version, "updated_at") and version.updated_at else None,
        )
        response = EngineVersionResponse(
            message="Engine version created successfully",
            code=status.HTTP_201_CREATED,
            object="engine.version",
            version=version_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating engine version: {e}")
        response = ErrorResponse(message="Error creating engine version", code=500)
    return response.to_http_response()


@engine_router.get("/version/")
async def get_engine_versions(
    engine_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Union[EngineVersionListResponse, ErrorResponse]:
    """Get engine versions with pagination."""
    try:
        result = EngineService.get_engine_versions(engine_id=engine_id, page=page, page_size=page_size)
        response = EngineVersionListResponse(
            message="Engine versions retrieved successfully",
            code=status.HTTP_200_OK,
            object="engine.version.list",
            **result,
        )
    except Exception as e:
        logger.error(f"Error retrieving engine versions: {e}")
        response = ErrorResponse(message="Error retrieving engine versions", code=500)
    return response.to_http_response()


@engine_router.get("/version/{version_id}")
async def get_engine_version(version_id: UUID) -> Union[EngineVersionResponse, ErrorResponse]:
    """Get an engine version by ID."""
    try:
        version = EngineService.get_engine_version(version_id)
        version_schema = schemas.EngineVersion(
            id=version.id,
            version=version.version,
            device_architecture=version.device_architecture,
            container_image=version.container_image,
            engine_id=version.engine_id,
            created_at=str(version.created_at) if hasattr(version, "created_at") and version.created_at else None,
            updated_at=str(version.updated_at) if hasattr(version, "updated_at") and version.updated_at else None,
        )
        response = EngineVersionResponse(
            message="Engine version retrieved successfully",
            code=status.HTTP_200_OK,
            object="engine.version",
            version=version_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving engine version: {e}")
        response = ErrorResponse(message="Error retrieving engine version", code=500)
    return response.to_http_response()


@engine_router.put("/version/{version_id}")
async def update_engine_version(
    version_id: UUID, version_data: EngineVersionUpdate
) -> Union[EngineVersionResponse, ErrorResponse]:
    """Update an engine version."""
    try:
        version = EngineService.update_engine_version(version_id, version_data)
        version_schema = schemas.EngineVersion(
            id=version.id,
            version=version.version,
            device_architecture=version.device_architecture,
            container_image=version.container_image,
            engine_id=version.engine_id,
            created_at=str(version.created_at) if hasattr(version, "created_at") and version.created_at else None,
            updated_at=str(version.updated_at) if hasattr(version, "updated_at") and version.updated_at else None,
        )
        response = EngineVersionResponse(
            message="Engine version updated successfully",
            code=status.HTTP_200_OK,
            object="engine.version",
            version=version_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating engine version: {e}")
        response = ErrorResponse(message="Error updating engine version", code=500)
    return response.to_http_response()


@engine_router.delete("/version/{version_id}")
async def delete_engine_version(version_id: UUID) -> Union[EngineVersionResponse, ErrorResponse]:
    """Delete an engine version."""
    try:
        EngineService.delete_engine_version(version_id)
        response = EngineVersionResponse(
            message="Engine version deleted successfully",
            code=status.HTTP_200_OK,
            object="engine.version",
            version=None,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting engine version: {e}")
        response = ErrorResponse(message="Error deleting engine version", code=500)
    return response.to_http_response()


# Engine Compatibility CRUD endpoints
@engine_router.post("/compatibility/")
async def create_engine_compatibility(
    compatibility_data: EngineCompatibilityCreate,
) -> Union[EngineCompatibilityResponse, ErrorResponse]:
    """Create a new engine compatibility."""
    try:
        compatibility = EngineService.create_engine_compatibility(compatibility_data)
        compatibility_schema = schemas.EngineCompatibility(
            id=compatibility.id,
            engine_version_id=compatibility.engine_version_id,
            architectures=compatibility.architectures,
            features=compatibility.features,
            created_at=str(compatibility.created_at)
            if hasattr(compatibility, "created_at") and compatibility.created_at
            else None,
            updated_at=str(compatibility.updated_at)
            if hasattr(compatibility, "updated_at") and compatibility.updated_at
            else None,
        )
        response = EngineCompatibilityResponse(
            message="Engine compatibility created successfully",
            code=status.HTTP_201_CREATED,
            object="engine.compatibility",
            compatibility=compatibility_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating engine compatibility: {e}")
        response = ErrorResponse(message="Error creating engine compatibility", code=500)
    return response.to_http_response()


@engine_router.put("/compatibility/{compatibility_id}")
async def update_engine_compatibility(
    compatibility_id: UUID, compatibility_data: EngineCompatibilityUpdate
) -> Union[EngineCompatibilityResponse, ErrorResponse]:
    """Update an engine compatibility."""
    try:
        compatibility = EngineService.update_engine_compatibility(compatibility_id, compatibility_data)
        compatibility_schema = schemas.EngineCompatibility(
            id=compatibility.id,
            engine_version_id=compatibility.engine_version_id,
            architectures=compatibility.architectures,
            features=compatibility.features,
            created_at=str(compatibility.created_at)
            if hasattr(compatibility, "created_at") and compatibility.created_at
            else None,
            updated_at=str(compatibility.updated_at)
            if hasattr(compatibility, "updated_at") and compatibility.updated_at
            else None,
        )
        response = EngineCompatibilityResponse(
            message="Engine compatibility updated successfully",
            code=status.HTTP_200_OK,
            object="engine.compatibility",
            compatibility=compatibility_schema,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating engine compatibility: {e}")
        response = ErrorResponse(message="Error updating engine compatibility", code=500)
    return response.to_http_response()


@engine_router.delete("/compatibility/{compatibility_id}")
async def delete_engine_compatibility(compatibility_id: UUID) -> Union[EngineCompatibilityResponse, ErrorResponse]:
    """Delete an engine compatibility."""
    try:
        EngineService.delete_engine_compatibility(compatibility_id)
        response = EngineCompatibilityResponse(
            message="Engine compatibility deleted successfully",
            code=status.HTTP_200_OK,
            object="engine.compatibility",
            compatibility=None,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting engine compatibility: {e}")
        response = ErrorResponse(message="Error deleting engine compatibility", code=500)
    return response.to_http_response()


@engine_router.get("/parser-rules/{engine_id}")
async def list_parser_rules(
    engine_id: UUID,
    rule_type: Optional[ParserRuleType] = None,
) -> Union[EngineParserRuleListResponse, ErrorResponse]:
    """List parser rules for a specific engine.

    Args:
        engine_id: The engine ID to list rules for.
        rule_type: Optional filter for rule type (tool or reasoning).
    """
    try:
        rules = EngineService.list_parser_rules(engine_id, rule_type=rule_type)
        rule_schemas = [_build_parser_rule_schema(rule) for rule in rules]

        response = EngineParserRuleListResponse(
            message="Parser rules retrieved successfully",
            code=status.HTTP_200_OK,
            object="engine.parser_rule.list",
            rules=rule_schemas,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error retrieving parser rules: {e}")
        response = ErrorResponse(message="Error retrieving parser rules", code=500)

    return response.to_http_response()


@engine_router.post("/parser-rules")
async def create_parser_rule(
    rule_data: EngineParserRuleCreate,
) -> Union[EngineParserRuleResponse, ErrorResponse]:
    """Create a new parser rule for an engine.

    The rule_type field determines whether this is a tool calling or reasoning parser rule.
    - tool: Requires parser_type OR chat_template
    - reasoning: Requires parser_type, chat_template NOT allowed
    """
    try:
        rule = EngineService.create_parser_rule(rule_data)
        response = EngineParserRuleResponse(
            message="Parser rule created successfully",
            code=status.HTTP_201_CREATED,
            object="engine.parser_rule",
            rule=_build_parser_rule_schema(rule),
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating parser rule: {e}")
        response = ErrorResponse(message="Error creating parser rule", code=500)

    return response.to_http_response()


@engine_router.put("/parser-rules/{rule_id}")
async def update_parser_rule(
    rule_id: UUID, rule_data: EngineParserRuleUpdate
) -> Union[EngineParserRuleResponse, ErrorResponse]:
    """Update an existing parser rule."""
    try:
        rule = EngineService.update_parser_rule(rule_id, rule_data)
        response = EngineParserRuleResponse(
            message="Parser rule updated successfully",
            code=status.HTTP_200_OK,
            object="engine.parser_rule",
            rule=_build_parser_rule_schema(rule),
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating parser rule: {e}")
        response = ErrorResponse(message="Error updating parser rule", code=500)

    return response.to_http_response()


@engine_router.delete("/parser-rules/{rule_id}")
async def delete_parser_rule(rule_id: UUID) -> Union[EngineParserRuleResponse, ErrorResponse]:
    """Delete a parser rule."""
    try:
        EngineService.delete_parser_rule(rule_id)
        response = EngineParserRuleResponse(
            message="Parser rule deleted successfully",
            code=status.HTTP_200_OK,
            object="engine.parser_rule",
            rule=None,
        )
    except ClientException as e:
        logger.error(f"Client exception: {e}")
        response = ErrorResponse(message=e.message, code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error deleting parser rule: {e}")
        response = ErrorResponse(message="Error deleting parser rule", code=500)

    return response.to_http_response()
