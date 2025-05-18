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

from typing import Optional

from budmicroframe.commons import logging
from fastapi import status

from ..engine.crud import EngineCRUD, EngineVersionCRUD
from .crud import ProviderCRUD
from .schemas import CompatibleModelsResponse, CompatibleProviders


logger = logging.get_logger(__name__)


class ModelService:
    """This class contains the services for the model API."""

    @staticmethod
    def get_compatible_models(
        engine: str,
        offset: int,
        limit: int,
        engine_version: Optional[str] = None,
    ) -> CompatibleModelsResponse:
        """Get the compatible models for a given model architecture and device architecture.

        Args:
            engine (str): The name of the engine.
            offset (int): The offset of the models.
            limit (int): The limit of the models.
            engine_version (str): The version of the engine.

        Returns:
            CompatibleModelsResponse: The compatible models.
        """
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

        # Get compatible providers from database
        total_providers = 0
        provider_details = []
        with ProviderCRUD() as provider_crud:
            total_providers, provider_details = provider_crud.get_compatible_providers(
                db_engine_version.id, offset, limit
            )

        # Create compatible providers response
        compatible_providers = {}
        for db_provider, db_model in provider_details:
            if str(db_provider.id) not in compatible_providers:
                compatible_providers[str(db_provider.id)] = CompatibleProviders(
                    id=db_provider.id,
                    name=db_provider.name,
                    provider_type=db_provider.provider_type,
                    icon=db_provider.icon,
                    description=db_provider.description,
                    models=[db_model] if db_model else [],
                )
            else:
                compatible_providers[str(db_provider.id)].models.append(db_model)

        return CompatibleModelsResponse(
            object="model.compatible",
            code=status.HTTP_200_OK,
            engine_name=engine,
            engine_version=db_engine_version.version,
            items=compatible_providers.values(),
            total_items=total_providers,
            page=offset,
            limit=limit,
        )
