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

"""The model schemas, containing essential data structures for the model microservice."""

from typing import Any, Dict, List

from pydantic import BaseModel

from ..commons.constants import ModalityEnum


class LiteLLMModelInfo(BaseModel):
    """Schema for LiteLLM model seeder."""

    uri: str
    config: Dict[str, Any]
    modality: List[ModalityEnum]


class ProviderCreate(BaseModel):
    """Schema for provider creation."""

    name: str
    provider_type: str
    icon: str
    description: str
