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

"""This module contains the services for the model API."""

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from fastapi import status
from sqlalchemy import Boolean
from sqlalchemy.exc import IntegrityError

from ..commons.constants import ProviderCapabilityEnum
from ..engine.crud import EngineCRUD, EngineVersionCRUD
from .crud import ModelArchitectureClassCRUD, ModelDetailsCRUD, ModelInfoCRUD, ProviderCRUD
from .models import ModelInfo, Provider
from .schemas import (
    CompatibleModelsResponse,
    CompatibleProviders,
    ModelArchitectureClassCreate,
    ModelArchitectureClassResponse,
    ModelArchitectureClassUpdate,
    ModelDetailsResponse,
    ModelDetailsUpdate,
    ModelInfoCreate,
    ModelInfoResponse,
    ModelInfoUpdate,
)


logger = logging.get_logger(__name__)


class ModelService:
    """This class contains the services for the model API."""

    @staticmethod
    def get_compatible_models(
        engine: Optional[str],
        offset: int,
        limit: int,
        engine_version: Optional[str] = None,
    ) -> CompatibleModelsResponse:
        """Get the compatible models for a given model architecture and device architecture.

        Args:
            engine (Optional[str]): The name of the engine. If None, returns all providers with models.
            offset (int): The offset of the models.
            limit (int): The limit of the models.
            engine_version (str): The version of the engine.

        Returns:
            CompatibleModelsResponse: The compatible models.
        """
        # If no engine is specified, return all providers with their models
        if engine is None:
            total_providers = 0
            compatible_providers = {}

            with ProviderCRUD() as provider_crud:
                total_providers, provider_details = provider_crud.get_all_providers_with_models(offset, limit)

                # Create compatible providers response while session is still active
                for db_provider, db_model in provider_details:
                    if str(db_provider.id) not in compatible_providers:
                        # Convert db_model to dict if it exists to avoid lazy loading issues
                        model_data = None
                        if db_model:
                            model_data = {
                                "id": db_model.id,
                                "uri": db_model.uri,
                                "modality": db_model.modality,
                                "provider_id": db_model.provider_id,
                                "input_cost": db_model.input_cost,
                                "output_cost": db_model.output_cost,
                                "cache_cost": db_model.cache_cost,
                                "search_context_cost_per_query": db_model.search_context_cost_per_query,
                                "tokens": db_model.tokens,
                                "rate_limits": db_model.rate_limits,
                                "media_limits": db_model.media_limits,
                                "features": db_model.features,
                                "endpoints": db_model.endpoints,
                                "deprecation_date": db_model.deprecation_date,
                                "chat_template": db_model.chat_template,
                                "tool_calling_parser_type": db_model.tool_calling_parser_type,
                            }

                        compatible_providers[str(db_provider.id)] = CompatibleProviders(
                            id=db_provider.id,
                            name=db_provider.name,
                            provider_type=db_provider.provider_type,
                            icon=db_provider.icon,
                            description=db_provider.description,
                            credentials=db_provider.credentials,
                            capabilities=db_provider.capabilities,
                            models=[ModelInfoResponse(**model_data)] if model_data else [],
                        )
                    else:
                        if db_model:
                            model_data = {
                                "id": db_model.id,
                                "uri": db_model.uri,
                                "modality": db_model.modality,
                                "provider_id": db_model.provider_id,
                                "input_cost": db_model.input_cost,
                                "output_cost": db_model.output_cost,
                                "cache_cost": db_model.cache_cost,
                                "search_context_cost_per_query": db_model.search_context_cost_per_query,
                                "tokens": db_model.tokens,
                                "rate_limits": db_model.rate_limits,
                                "media_limits": db_model.media_limits,
                                "features": db_model.features,
                                "endpoints": db_model.endpoints,
                                "deprecation_date": db_model.deprecation_date,
                                "chat_template": db_model.chat_template,
                                "tool_calling_parser_type": db_model.tool_calling_parser_type,
                            }
                            compatible_providers[str(db_provider.id)].models.append(ModelInfoResponse(**model_data))

            return CompatibleModelsResponse(
                object="model.compatible",
                code=status.HTTP_200_OK,
                engine_name=None,
                engine_version=None,
                items=compatible_providers.values(),
                total_items=total_providers,
                page=(offset // limit) + 1,
                limit=limit,
            )

        # Get engine from database
        db_engine = None
        with EngineCRUD() as engine_crud:
            db_engine = engine_crud.fetch_one({"name": engine})
        if not db_engine:
            logger.warning(f"Engine {engine} not found")
            return CompatibleModelsResponse(
                object="model.compatible",
                code=status.HTTP_200_OK,
                engine_name=engine,
                engine_version=engine_version,
                items=[],
                total_items=0,
                page=offset,
                limit=limit,
            )

        # Get engine version from database
        db_engine_version = None
        with EngineVersionCRUD() as engine_version_crud:
            if engine_version:
                db_engine_version = engine_version_crud.fetch_one(
                    {"version": engine_version, "engine_id": db_engine.id}
                )
            else:
                db_engine_version = engine_version_crud.get_latest_engine_version(db_engine.id)

        if not db_engine_version:
            logger.warning(f"Engine version {engine_version} not found")
            return CompatibleModelsResponse(
                object="model.compatible",
                code=status.HTTP_200_OK,
                engine_name=engine,
                engine_version=engine_version,
                items=[],
                total_items=0,
                page=offset,
                limit=limit,
            )

        logger.info(f"Engine version {db_engine_version} found")

        # Get compatible providers from database and create response within session
        total_providers = 0
        compatible_providers = {}

        with ProviderCRUD() as provider_crud:
            total_providers, provider_details = provider_crud.get_compatible_providers_with_capability(
                db_engine_version.id, ProviderCapabilityEnum.MODEL, offset, limit
            )

            # Create compatible providers response while session is still active
            for db_provider, db_model in provider_details:
                if str(db_provider.id) not in compatible_providers:
                    # Convert db_model to dict if it exists to avoid lazy loading issues
                    model_data = None
                    if db_model:
                        model_data = {
                            "id": db_model.id,
                            "uri": db_model.uri,
                            "modality": db_model.modality,
                            "provider_id": db_model.provider_id,
                            "input_cost": db_model.input_cost,
                            "output_cost": db_model.output_cost,
                            "cache_cost": db_model.cache_cost,
                            "search_context_cost_per_query": db_model.search_context_cost_per_query,
                            "tokens": db_model.tokens,
                            "rate_limits": db_model.rate_limits,
                            "media_limits": db_model.media_limits,
                            "features": db_model.features,
                            "endpoints": db_model.endpoints,
                            "deprecation_date": db_model.deprecation_date,
                            "chat_template": db_model.chat_template,
                        }

                    compatible_providers[str(db_provider.id)] = CompatibleProviders(
                        id=db_provider.id,
                        name=db_provider.name,
                        provider_type=db_provider.provider_type,
                        icon=db_provider.icon,
                        description=db_provider.description,
                        credentials=db_provider.credentials,
                        capabilities=db_provider.capabilities,
                        models=[ModelInfoResponse(**model_data)] if model_data else [],
                    )
                else:
                    if db_model:
                        model_data = {
                            "id": db_model.id,
                            "uri": db_model.uri,
                            "modality": db_model.modality,
                            "provider_id": db_model.provider_id,
                            "input_cost": db_model.input_cost,
                            "output_cost": db_model.output_cost,
                            "cache_cost": db_model.cache_cost,
                            "search_context_cost_per_query": db_model.search_context_cost_per_query,
                            "tokens": db_model.tokens,
                            "rate_limits": db_model.rate_limits,
                            "media_limits": db_model.media_limits,
                            "features": db_model.features,
                            "endpoints": db_model.endpoints,
                            "deprecation_date": db_model.deprecation_date,
                            "chat_template": db_model.chat_template,
                        }
                        compatible_providers[str(db_provider.id)].models.append(ModelInfoResponse(**model_data))

        return CompatibleModelsResponse(
            object="model.compatible",
            code=status.HTTP_200_OK,
            engine_name=engine,
            engine_version=db_engine_version.version,
            items=compatible_providers.values(),
            total_items=total_providers,
            page=(offset // limit) + 1,
            limit=limit,
        )

    @staticmethod
    def get_model_details(model_uri: str) -> Optional[ModelDetailsResponse]:
        """Get detailed information for a specific model by URI.

        Args:
            model_uri: The URI of the model to get details for.

        Returns:
            ModelDetailsResponse if found, None otherwise.
        """
        with ModelDetailsCRUD() as model_details_crud:
            combined_data = model_details_crud.get_by_model_uri(model_uri)
            if combined_data:
                return ModelDetailsResponse(**combined_data)
            return None

    @staticmethod
    def get_all_models(
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        provider_id: Optional[UUID] = None,
        supports_lora: Optional[bool] = None,
        supports_pipeline_parallelism: Optional[bool] = None,
    ) -> Tuple[List[ModelInfoResponse], int]:
        """Get all models with pagination and optional filtering.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            search: Optional search term to filter by URI
            provider_id: Optional provider ID to filter by
            supports_lora: Optional filter for LoRA support
            supports_pipeline_parallelism: Optional filter for pipeline parallelism support

        Returns:
            Tuple of (list of models, total count)
        """
        with ModelInfoCRUD() as crud:
            session = crud.get_session()
            try:
                # Build base query with provider and license info
                from .models import License

                query = (
                    session.query(
                        ModelInfo,
                        Provider.name.label("provider_name"),
                        Provider.provider_type.label("provider_type"),
                        License,
                    )
                    .join(Provider, ModelInfo.provider_id == Provider.id)
                    .outerjoin(License, ModelInfo.license_id == License.id)
                )

                # Apply filters
                if search:
                    search_pattern = f"%{search}%"
                    query = query.filter(ModelInfo.uri.ilike(search_pattern))

                if provider_id:
                    query = query.filter(ModelInfo.provider_id == provider_id)

                # Apply JSONB feature filters
                if supports_lora is not None:
                    query = query.filter(ModelInfo.features["supports_lora"].astext.cast(Boolean) == supports_lora)

                if supports_pipeline_parallelism is not None:
                    query = query.filter(
                        ModelInfo.features["supports_pipeline_parallelism"].astext.cast(Boolean)
                        == supports_pipeline_parallelism
                    )

                # Get total count
                total = query.count()

                # Sort by created_at date (newest first)
                query = query.order_by(ModelInfo.created_at.desc())

                # Apply pagination
                offset = (page - 1) * page_size
                results = query.offset(offset).limit(page_size).all()

                # Convert to response format
                models = []
                for model, provider_name, provider_type, license in results:
                    model_dict = {
                        "id": model.id,
                        "uri": model.uri,
                        "modality": model.modality or [],
                        "provider_id": model.provider_id,
                        "provider_name": provider_name,
                        "provider_type": provider_type,
                        "input_cost": model.input_cost,
                        "output_cost": model.output_cost,
                        "cache_cost": model.cache_cost,
                        "search_context_cost_per_query": model.search_context_cost_per_query,
                        "tokens": model.tokens,
                        "rate_limits": model.rate_limits,
                        "media_limits": model.media_limits,
                        "features": model.features,
                        "endpoints": model.endpoints or [],
                        "deprecation_date": model.deprecation_date,
                        "license": license,
                        "chat_template": model.chat_template,
                        "tool_calling_parser_type": model.tool_calling_parser_type,
                        "created_at": model.created_at,
                        "modified_at": model.modified_at,
                    }
                    models.append(ModelInfoResponse(**model_dict))

                return models, total
            finally:
                crud.cleanup_session(session)

    @staticmethod
    def get_model_by_id(model_id: UUID) -> ModelInfoResponse:
        """Get a model by its ID.

        Args:
            model_id: UUID of the model

        Returns:
            Model object

        Raises:
            ClientException: If model not found
        """
        with ModelInfoCRUD() as crud:
            session = crud.get_session()
            try:
                # Query model with provider and license info
                from .models import License

                result = (
                    session.query(
                        ModelInfo,
                        Provider.name.label("provider_name"),
                        Provider.provider_type.label("provider_type"),
                        License,
                    )
                    .join(Provider, ModelInfo.provider_id == Provider.id)
                    .outerjoin(License, ModelInfo.license_id == License.id)
                    .filter(ModelInfo.id == model_id)
                    .first()
                )

                if not result:
                    raise ClientException(message=f"Model with ID {model_id} not found", status_code=404)

                model, provider_name, provider_type, license = result
                model_dict = {
                    "id": model.id,
                    "uri": model.uri,
                    "modality": model.modality or [],
                    "provider_id": model.provider_id,
                    "provider_name": provider_name,
                    "provider_type": provider_type,
                    "input_cost": model.input_cost,
                    "output_cost": model.output_cost,
                    "cache_cost": model.cache_cost,
                    "search_context_cost_per_query": model.search_context_cost_per_query,
                    "tokens": model.tokens,
                    "rate_limits": model.rate_limits,
                    "media_limits": model.media_limits,
                    "features": model.features,
                    "endpoints": model.endpoints or [],
                    "deprecation_date": model.deprecation_date,
                    "license": license,
                    "chat_template": model.chat_template,
                    "tool_calling_parser_type": model.tool_calling_parser_type,
                    "created_at": model.created_at,
                    "modified_at": model.modified_at,
                }
                return ModelInfoResponse(**model_dict)
            finally:
                crud.cleanup_session(session)

    @staticmethod
    def create_model(model_data: ModelInfoCreate) -> ModelInfoResponse:
        """Create a new model.

        Args:
            model_data: Model creation data

        Returns:
            Created model object

        Raises:
            ClientException: If URI already exists or provider not found
        """
        with ModelInfoCRUD() as crud:
            # Check if URI already exists
            existing = crud.fetch_one({"uri": model_data.uri})
            if existing:
                raise ClientException(message=f"Model with URI '{model_data.uri}' already exists", status_code=400)

            # Verify provider exists
            with ProviderCRUD() as provider_crud:
                provider = provider_crud.fetch_one({"id": model_data.provider_id})
                if not provider:
                    raise ClientException(
                        message=f"Provider with ID {model_data.provider_id} not found", status_code=404
                    )

            try:
                # Create the model
                model_dict = model_data.model_dump()
                created_model_id = crud.upsert(model_dict)

                # Return with provider info
                return ModelService.get_model_by_id(created_model_id)
            except IntegrityError as e:
                logger.error(f"Integrity error creating model: {e}")
                raise ClientException(message="Failed to create model due to data conflict", status_code=400) from e

    @staticmethod
    def update_model(model_id: UUID, model_data: ModelInfoUpdate) -> ModelInfoResponse:
        """Update a model.

        Args:
            model_id: UUID of the model to update
            model_data: Update data

        Returns:
            Updated model object

        Raises:
            ClientException: If model not found
        """
        with ModelInfoCRUD() as crud:
            model = crud.fetch_one({"id": model_id})
            if not model:
                raise ClientException(message=f"Model with ID {model_id} not found", status_code=404)

            # If updating provider, verify it exists
            if model_data.provider_id:
                with ProviderCRUD() as provider_crud:
                    provider = provider_crud.fetch_one({"id": model_data.provider_id})
                    if not provider:
                        raise ClientException(
                            message=f"Provider with ID {model_data.provider_id} not found", status_code=404
                        )

            # If updating URI, check it's not taken
            if model_data.uri and model_data.uri != model.uri:
                existing = crud.fetch_one({"uri": model_data.uri})
                if existing:
                    raise ClientException(message=f"Model with URI '{model_data.uri}' already exists", status_code=400)

            # Update the model
            update_dict = model_data.model_dump(exclude_unset=True)
            if update_dict:
                session = crud.get_session()
                try:
                    # Update the model attributes
                    for key, value in update_dict.items():
                        setattr(model, key, value)
                    session.add(model)
                    session.commit()
                finally:
                    crud.cleanup_session(session)

            return ModelService.get_model_by_id(model_id)

    @staticmethod
    def delete_model(model_id: UUID) -> None:
        """Delete a model.

        Args:
            model_id: UUID of the model to delete

        Raises:
            ClientException: If model not found or has dependencies
        """
        from sqlalchemy import text

        from ..model.models import ModelDetails

        with ModelInfoCRUD() as crud:
            session = crud.get_session()
            try:
                # Check if model exists
                model = session.query(ModelInfo).filter(ModelInfo.id == model_id).first()
                if not model:
                    raise ClientException(message=f"Model with ID {model_id} not found", status_code=404)

                # Delete engine compatibility entries (cascade delete)
                engine_compat_deleted = session.execute(
                    text("DELETE FROM engine_version_model_info WHERE model_info_id = :model_id"),
                    {"model_id": model_id},
                ).rowcount

                if engine_compat_deleted > 0:
                    logger.info(f"Deleted {engine_compat_deleted} engine compatibility entries for model {model_id}")

                # Delete associated model_details
                details_deleted = session.query(ModelDetails).filter(ModelDetails.model_info_id == model_id).delete()
                if details_deleted > 0:
                    logger.info(f"Deleted {details_deleted} model_details entries for model {model_id}")

                # Delete the model itself
                session.delete(model)
                session.commit()
                logger.info(f"Successfully deleted model {model_id} ({model.uri})")

            except ClientException:
                session.rollback()
                raise
            except Exception as e:
                session.rollback()
                logger.error(f"Error deleting model {model_id}: {e}")
                # Check if it's a foreign key constraint error
                error_msg = str(e)
                if "foreign" in error_msg.lower() or "constraint" in error_msg.lower():
                    # Try to extract table name from error message
                    if "table" in error_msg:
                        raise ClientException(
                            message=f"Cannot delete model because it has dependencies. Database error: {error_msg}",
                            status_code=400,
                        ) from e
                    raise ClientException(
                        message="Cannot delete model because it has dependencies in other tables", status_code=400
                    ) from e
                raise ClientException(message=f"Failed to delete model: {str(e)}", status_code=500) from e
            finally:
                crud.cleanup_session(session)

    @staticmethod
    def update_model_details(model_id: UUID, details_data: ModelDetailsUpdate) -> ModelDetailsResponse:
        """Update model details including description, features, and pricing.

        Args:
            model_id: UUID of the model
            details_data: Details update data

        Returns:
            Updated model details

        Raises:
            ClientException: If model not found
        """
        from .models import License, ModelDetails

        with ModelInfoCRUD() as crud:
            session = crud.get_session()
            try:
                # Check if model exists
                model = session.query(ModelInfo).filter(ModelInfo.id == model_id).first()
                if not model:
                    raise ClientException(message=f"Model with ID {model_id} not found", status_code=404)

                # Check if details already exist
                details = session.query(ModelDetails).filter(ModelDetails.model_info_id == model_id).first()

                # Update or create details
                if details:
                    # Update existing details fields
                    if details_data.description is not None:
                        details.description = details_data.description
                    if details_data.advantages is not None:
                        details.advantages = details_data.advantages
                    if details_data.disadvantages is not None:
                        details.disadvantages = details_data.disadvantages
                    if details_data.use_cases is not None:
                        details.use_cases = details_data.use_cases
                    if details_data.tags is not None:
                        details.tags = details_data.tags
                else:
                    # Create new details entry
                    details = ModelDetails(
                        model_info_id=model_id,
                        description=details_data.description,
                        advantages=details_data.advantages,
                        disadvantages=details_data.disadvantages,
                        use_cases=details_data.use_cases,
                        tags=details_data.tags,
                    )
                    session.add(details)

                # Update model pricing and features
                update_dict = {}
                if details_data.input_cost is not None:
                    update_dict["input_cost"] = details_data.input_cost.model_dump(exclude_none=True) or None
                if details_data.output_cost is not None:
                    update_dict["output_cost"] = details_data.output_cost.model_dump(exclude_none=True) or None
                if details_data.cache_cost is not None:
                    update_dict["cache_cost"] = details_data.cache_cost.model_dump(exclude_none=True) or None
                if details_data.search_context_cost_per_query is not None:
                    update_dict["search_context_cost_per_query"] = (
                        details_data.search_context_cost_per_query.model_dump(exclude_none=True) or None
                    )
                if details_data.tokens is not None:
                    update_dict["tokens"] = details_data.tokens.model_dump(exclude_none=True) or None
                if details_data.rate_limits is not None:
                    update_dict["rate_limits"] = details_data.rate_limits.model_dump(exclude_none=True) or None
                if details_data.media_limits is not None:
                    update_dict["media_limits"] = details_data.media_limits.model_dump(exclude_none=True) or None
                if details_data.features is not None:
                    update_dict["features"] = details_data.features.model_dump(exclude_none=True) or None

                # Update model fields
                for key, value in update_dict.items():
                    setattr(model, key, value)

                session.commit()

                # Get provider and license info for response
                provider = session.query(Provider).filter(Provider.id == model.provider_id).first()
                license = (
                    session.query(License).filter(License.id == model.license_id).first() if model.license_id else None
                )

                # Prepare response
                response_dict = {
                    "id": details.id if details else None,
                    "model_info_id": model_id,
                    "description": details.description if details else None,
                    "advantages": details.advantages if details else None,
                    "disadvantages": details.disadvantages if details else None,
                    "use_cases": details.use_cases if details else None,
                    "evaluations": details.evaluations if details else None,
                    "languages": details.languages if details else None,
                    "tags": details.tags if details else None,
                    "tasks": details.tasks if details else None,
                    "papers": details.papers if details else None,
                    "github_url": details.github_url if details else None,
                    "website_url": details.website_url if details else None,
                    "logo_url": details.logo_url if details else None,
                    "architecture": details.architecture if details else None,
                    "model_tree": details.model_tree if details else None,
                    "extraction_metadata": details.extraction_metadata if details else None,
                    "created_at": details.created_at if details else model.created_at,
                    "modified_at": details.modified_at if details else model.modified_at,
                    "uri": model.uri,
                    "modality": model.modality or [],
                    "input_cost": model.input_cost,
                    "output_cost": model.output_cost,
                    "cache_cost": model.cache_cost,
                    "search_context_cost_per_query": model.search_context_cost_per_query,
                    "tokens": model.tokens,
                    "rate_limits": model.rate_limits,
                    "media_limits": model.media_limits,
                    "features": model.features,
                    "endpoints": model.endpoints or [],
                    "deprecation_date": model.deprecation_date,
                    "license": license,
                    "tool_calling_parser_type": model.tool_calling_parser_type,
                    "provider_name": provider.name if provider else None,
                    "provider_type": provider.provider_type if provider else None,
                }

                return ModelDetailsResponse(**response_dict)

            except ClientException:
                session.rollback()
                raise
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating model details for {model_id}: {e}")
                raise ClientException(message=f"Failed to update model details: {str(e)}", status_code=500) from e
            finally:
                crud.cleanup_session(session)

    # Architecture methods
    @staticmethod
    def get_all_architectures(
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all architectures with pagination and search.

        Args:
            page: Page number (starts from 1)
            page_size: Number of items per page
            search: Optional search term

        Returns:
            Tuple of (architectures list, total count)
        """
        crud = ModelArchitectureClassCRUD()
        offset = (page - 1) * page_size

        try:
            architectures, total = crud.get_all_with_model_count(
                offset=offset,
                limit=page_size,
                search=search,
            )
            return architectures, total
        except Exception as e:
            logger.error(f"Error fetching architectures: {e}")
            raise ClientException(message=f"Failed to fetch architectures: {str(e)}", status_code=500) from e

    @staticmethod
    def get_architecture_by_id(architecture_id: UUID) -> Optional[ModelArchitectureClassResponse]:
        """Get architecture by ID.

        Args:
            architecture_id: UUID of the architecture

        Returns:
            Architecture or None if not found
        """
        crud = ModelArchitectureClassCRUD()

        try:
            architecture = crud.fetch_one({"id": architecture_id})
            if architecture:
                return ModelArchitectureClassResponse(
                    id=architecture.id,
                    class_name=architecture.class_name,
                    architecture_family=architecture.architecture_family,
                    tool_calling_parser_type=architecture.tool_calling_parser_type,
                    reasoning_parser_type=architecture.reasoning_parser_type,
                    created_at=architecture.created_at,
                    modified_at=architecture.modified_at,
                )
            return None
        except Exception as e:
            logger.error(f"Error fetching architecture {architecture_id}: {e}")
            raise ClientException(message=f"Failed to fetch architecture: {str(e)}", status_code=500) from e

    @staticmethod
    def create_architecture(
        architecture_data: ModelArchitectureClassCreate,
    ) -> ModelArchitectureClassResponse:
        """Create a new architecture.

        Args:
            architecture_data: Architecture creation data

        Returns:
            Created architecture
        """
        crud = ModelArchitectureClassCRUD()

        try:
            architecture = crud.insert(architecture_data.model_dump())
            return ModelArchitectureClassResponse(
                id=architecture.id,
                class_name=architecture.class_name,
                architecture_family=architecture.architecture_family,
                tool_calling_parser_type=architecture.tool_calling_parser_type,
                reasoning_parser_type=architecture.reasoning_parser_type,
                created_at=architecture.created_at,
                modified_at=architecture.modified_at,
            )
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ClientException(
                    message=f"Architecture with class_name '{architecture_data.class_name}' already exists",
                    status_code=status.HTTP_409_CONFLICT,
                ) from e
            raise ClientException(message=f"Failed to create architecture: {str(e)}", status_code=500) from e
        except Exception as e:
            logger.error(f"Error creating architecture: {e}")
            raise ClientException(message=f"Failed to create architecture: {str(e)}", status_code=500) from e

    @staticmethod
    def update_architecture(
        architecture_id: UUID,
        architecture_data: ModelArchitectureClassUpdate,
    ) -> Optional[ModelArchitectureClassResponse]:
        """Update an architecture.

        Args:
            architecture_id: UUID of the architecture to update
            architecture_data: Update data

        Returns:
            Updated architecture or None if not found
        """
        crud = ModelArchitectureClassCRUD()

        try:
            # Check if architecture exists
            existing = crud.fetch_one({"id": architecture_id})
            if not existing:
                return None

            # Update architecture
            update_count = crud.update(architecture_data.model_dump(exclude_unset=True), {"id": architecture_id})

            if update_count > 0:
                # Fetch the updated architecture
                updated = crud.fetch_one({"id": architecture_id})
                if updated:
                    return ModelArchitectureClassResponse(
                        id=updated.id,
                        class_name=updated.class_name,
                        architecture_family=updated.architecture_family,
                        tool_calling_parser_type=updated.tool_calling_parser_type,
                        reasoning_parser_type=updated.reasoning_parser_type,
                        created_at=updated.created_at,
                        modified_at=updated.modified_at,
                    )
            return None
        except Exception as e:
            logger.error(f"Error updating architecture {architecture_id}: {e}")
            raise ClientException(message=f"Failed to update architecture: {str(e)}", status_code=500) from e

    @staticmethod
    def delete_architecture(architecture_id: UUID) -> bool:
        """Delete an architecture.

        Args:
            architecture_id: UUID of the architecture to delete

        Returns:
            True if deleted, False if not found
        """
        crud = ModelArchitectureClassCRUD()

        try:
            # Check if architecture exists
            existing = crud.fetch_one({"id": architecture_id})
            if not existing:
                return False

            # Check if any models are using this architecture
            model_crud = ModelInfoCRUD()
            models_using = model_crud.fetch_many({"model_architecture_class_id": architecture_id})[0]
            if models_using:
                raise ClientException(
                    message=f"Cannot delete architecture: {len(models_using)} models are using it",
                    status_code=status.HTTP_409_CONFLICT,
                )

            # Delete architecture
            crud.delete({"id": architecture_id})
            return True
        except ClientException:
            raise
        except Exception as e:
            logger.error(f"Error deleting architecture {architecture_id}: {e}")
            raise ClientException(message=f"Failed to delete architecture: {str(e)}", status_code=500) from e
