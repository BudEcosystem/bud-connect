from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from budmicroframe.commons.schemas import SuccessResponse
from pydantic import BaseModel, model_validator


class DeviceArchitecture(Enum):
    CUDA = "CUDA"
    ROCM = "ROCM"
    CPU = "CPU"
    HPU = "HPU"


class ParserMatchType(Enum):
    EXACT = "exact"
    PREFIX = "prefix"
    REGEX = "regex"


class ParserRuleType(Enum):
    TOOL = "tool"
    REASONING = "reasoning"


class Engine(BaseModel):
    id: UUID
    name: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        """Configuration for the Engine model."""

        from_attributes = True


class EngineCreate(BaseModel):
    name: str


class EngineUpdate(BaseModel):
    name: Optional[str] = None


class EngineVersion(BaseModel):
    id: UUID
    version: str
    device_architecture: DeviceArchitecture
    container_image: str
    engine_id: UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        """Configuration for the Engine model."""

        from_attributes = True


class EngineVersionCreate(BaseModel):
    version: str
    device_architecture: DeviceArchitecture
    container_image: str
    engine_id: UUID


class EngineVersionUpdate(BaseModel):
    version: Optional[str] = None
    device_architecture: Optional[DeviceArchitecture] = None
    container_image: Optional[str] = None


class ModelArchitecture(BaseModel):
    name: str


class Feature(BaseModel):
    name: str


class EngineCompatibility(BaseModel):
    id: UUID
    engine_version_id: UUID
    architectures: Dict[str, Any]
    features: Dict[str, Any]
    supported_tool_calling_parser_types: Optional[Dict[str, Any]] = None
    supported_reasoning_parsers: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        """Configuration for the Engine model."""

        from_attributes = True


class EngineCompatibilityCreate(BaseModel):
    engine_version_id: UUID
    architectures: Dict[str, Any]
    features: Dict[str, Any]
    supported_tool_calling_parser_types: Optional[Dict[str, Any]] = None
    supported_reasoning_parsers: Optional[Dict[str, Any]] = None


class EngineCompatibilityUpdate(BaseModel):
    architectures: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None
    supported_tool_calling_parser_types: Optional[Dict[str, Any]] = None
    supported_reasoning_parsers: Optional[Dict[str, Any]] = None


class LatestEngineVersion(BaseModel):
    version: str
    compatibilities: List[EngineCompatibility]


class LatestEngineVersionResponse(SuccessResponse, LatestEngineVersion):
    pass


class CompatibleEngine(BaseModel):
    engine: str
    device_architecture: DeviceArchitecture
    version: str
    container_image: str
    engine_version_id: Optional[UUID] = None
    engine_id: Optional[UUID] = None
    tool_calling_parser_type: Optional[str] = None
    reasoning_parser_type: Optional[str] = None
    architecture_family: Optional[str] = None
    chat_template: Optional[str] = None
    parser_source: Optional[str] = None
    parser_notes: Optional[str] = None
    supports_lora: Optional[bool] = None
    supports_pipeline_parallelism: Optional[bool] = None


class CompatibleEnginesResponse(SuccessResponse):
    compatible_engines: List[CompatibleEngine]


class EngineParserRuleBase(BaseModel):
    engine_id: UUID
    rule_type: ParserRuleType = ParserRuleType.TOOL
    parser_type: Optional[str] = None
    match_type: ParserMatchType
    pattern: str
    priority: Optional[int] = 0
    enabled: Optional[bool] = True
    notes: Optional[str] = None
    chat_template: Optional[str] = None


class EngineParserRuleCreate(EngineParserRuleBase):
    @model_validator(mode="after")
    def _validate_rule_type_constraints(self) -> "EngineParserRuleCreate":
        parser_type = self.parser_type.strip() if isinstance(self.parser_type, str) else self.parser_type
        chat_template = self.chat_template.strip() if isinstance(self.chat_template, str) else self.chat_template

        if self.rule_type == ParserRuleType.TOOL:
            if not parser_type and not chat_template:
                raise ValueError("Either parser_type or chat_template must be provided for tool rules")
        elif self.rule_type == ParserRuleType.REASONING:
            if not parser_type:
                raise ValueError("parser_type is required for reasoning rules")
            if chat_template:
                raise ValueError("chat_template is not allowed for reasoning rules")

        self.parser_type = parser_type or None
        self.chat_template = chat_template or None
        return self


class EngineParserRuleUpdate(BaseModel):
    rule_type: Optional[ParserRuleType] = None
    parser_type: Optional[str] = None
    match_type: Optional[ParserMatchType] = None
    pattern: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None
    notes: Optional[str] = None
    chat_template: Optional[str] = None


class EngineParserRule(BaseModel):
    id: UUID
    engine_id: UUID
    rule_type: ParserRuleType
    parser_type: Optional[str] = None
    match_type: ParserMatchType
    pattern: str
    priority: Optional[int] = 0
    enabled: bool
    notes: Optional[str] = None
    chat_template: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class EngineParserRuleResponse(SuccessResponse):
    rule: Optional[EngineParserRule] = None


class EngineParserRuleListResponse(SuccessResponse):
    rules: List[EngineParserRule]


class EngineListResponse(SuccessResponse):
    engines: List[Engine]
    total: int
    page: int
    page_size: int


class EngineResponse(SuccessResponse):
    engine: Optional[Engine] = None


class EngineVersionListResponse(SuccessResponse):
    versions: List[EngineVersion]
    total: int
    page: int
    page_size: int


class EngineVersionResponse(SuccessResponse):
    version: Optional[EngineVersion] = None


class EngineCompatibilityResponse(SuccessResponse):
    compatibility: Optional[EngineCompatibility] = None
