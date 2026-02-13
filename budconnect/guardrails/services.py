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

"""Business logic services for guardrail operations."""

from typing import Optional

from budmicroframe.commons import logging
from fastapi import status
from pydantic import UUID4

from ..commons.constants import ProviderCapabilityEnum
from ..engine.crud import EngineCRUD, EngineVersionCRUD
from ..model.crud import ProviderCRUD
from .crud import GuardrailProbeCRUD, GuardrailRuleCRUD
from .schemas import CompatibleProbesResponse, CompatibleProviders, GuardrailProbeResponse, GuardrailRuleResponse


logger = logging.get_logger(__name__)


class GuardrailService:
    @staticmethod
    def get_compatible_probes(
        engine: str,
        offset: int,
        limit: int,
        engine_version: Optional[str] = None,
    ) -> CompatibleProbesResponse:
        """Get the compatible guardrail probes for a given engine.

        Args:
            engine: The name of the engine.
            offset: The offset of the probes.
            limit: The limit of the probes.
            engine_version: The version of the engine.

        Returns:
            CompatibleProbesResponse: The compatible probes with their providers.
        """
        page = (offset // limit) + 1

        # Get engine from database
        db_engine = None
        with EngineCRUD() as engine_crud:
            db_engine = engine_crud.fetch_one({"name": engine})
        if not db_engine:
            logger.warning(f"Engine {engine} not found")
            return CompatibleProbesResponse(
                object="guardrail.compatible",
                code=status.HTTP_200_OK,
                engine_name=engine,
                engine_version=engine_version,
                items=[],
                total_items=0,
                page=page,
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
            return CompatibleProbesResponse(
                object="guardrail.compatible",
                code=status.HTTP_200_OK,
                engine_name=engine,
                engine_version=engine_version,
                items=[],
                total_items=0,
                page=page,
                limit=limit,
            )

        logger.info(f"Engine version {db_engine_version} found")

        # Get providers that have moderation capability
        compatible_providers = []
        total_providers_with_moderation = 0

        with ProviderCRUD() as provider_crud:
            # Get providers that have moderation capability and are compatible with the engine version
            total_providers_with_moderation, providers_with_moderation = provider_crud.get_providers_by_capability(
                db_engine_version.id, ProviderCapabilityEnum.MODERATION, offset, limit
            )

        with GuardrailProbeCRUD() as probe_crud:
            session = probe_crud.get_session()
            try:
                # For each provider, get their guardrail probes
                for db_provider in providers_with_moderation:
                    # Get all guardrail probes for this provider with correct pagination
                    total_probes, probes_with_details = probe_crud.get_compatible_providers(
                        db_provider.id, 0, 1000, session=session
                    )

                    # Convert probes to response format
                    probe_responses = []
                    for probe in probes_with_details:
                        probe_response = GuardrailProbeResponse(
                            id=probe.id,
                            name=probe.name,
                            uri=probe.uri,
                            provider_id=probe.provider_id,
                            description=probe.description,
                            icon=probe.icon,
                            tags=probe.tags,
                            deprecation_date=probe.deprecation_date,
                            examples=probe.examples,
                            guard_types=probe.guard_types,
                            scanner_types=probe.scanner_types,
                            modality_types=probe.modality_types,
                            rules_count=getattr(probe, "rules_count", 0),
                        )
                        probe_responses.append(probe_response)

                    provider_response = CompatibleProviders(
                        id=db_provider.id,
                        name=db_provider.name,
                        provider_type=db_provider.provider_type,
                        icon=db_provider.icon,
                        description=db_provider.description,
                        credentials=db_provider.credentials,
                        capabilities=db_provider.capabilities,
                        probes=probe_responses,
                    )
                    compatible_providers.append(provider_response)
            finally:
                probe_crud.cleanup_session(session)

        return CompatibleProbesResponse(
            object="guardrail.compatible",
            code=status.HTTP_200_OK,
            engine_name=engine,
            engine_version=db_engine_version.version,
            items=compatible_providers,
            total_items=total_providers_with_moderation,
            page=page,
            limit=limit,
        )

    @staticmethod
    def get_probe_rules(probe_id: UUID4, offset: int, limit: int) -> Optional[GuardrailRuleResponse]:
        """Get detailed information for a specific guardrail probe including its rules.

        Args:
            probe_id: The ID of the probe to get details for.

        Returns:
            GuardrailRuleResponse if found, None otherwise.
        """
        with GuardrailRuleCRUD() as probe_crud:
            # Get probe details with rules using the get_by_probe_id method
            combined_data = probe_crud.get_by_probe_id(probe_id, offset=offset, limit=limit)
            if combined_data:
                return GuardrailRuleResponse(
                    **combined_data, page=(offset // limit) + 1, limit=limit, object="guardrail.rule"
                )
            return None
