import re
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from budmicroframe.commons.schemas import SuccessResponse
from pydantic import BaseModel, Field, field_validator, model_validator


#: The KV-cache features an engine build can list (bud-runtime FRD-023). budsim and budcluster render a KV setting --
#: KV events, the cache salt, the CPU tier in register (``cpu_offload_shm``) or alloc (``cpu_offload_host_alloc``)
#: mode or with per-copy transfers, FP8 KV, the fs tier -- only for the features the build lists, so a build lists one
#: only after it was verified on that build. The set must match the simulator's ``KV_FEATURES``
#: (llm_memory_calculator/engine/record.py) one for one: an unknown name renders nothing downstream.
KV_FEATURES = frozenset(
    {
        "kv_events",
        "cache_salt",
        "cpu_offload_shm",
        "cpu_offload_host_alloc",
        "cpu_offload_shm_per_copy",
        "kv_fp8",
        "tiering_fs",
    }
)

#: An upstream vLLM version: a release (``0.31.0``), a minor (``0.30``), a release candidate (``0.31.0rc1``) or a dev
#: build with its commit (``0.26.0.dev+481e481be``). The planner matches it by minor.
_UPSTREAM_VLLM = re.compile(r"^\d+\.\d+(\.\d+)?([a-z]+\d*)?(\.dev\d*)?(\+[0-9a-z.]+)?$")


def check_kv_features(value: Optional[List[str]]) -> Optional[List[str]]:
    """Validate the names against ``KV_FEATURES``; return them deduplicated and sorted (None stays None)."""
    if value is None:
        return None
    names = [str(v).strip() for v in value]
    unknown = sorted(set(names) - KV_FEATURES)
    if unknown:
        raise ValueError(f"unknown kv_features {unknown}; known: {sorted(KV_FEATURES)}")
    return sorted(set(names))


def check_upstream_vllm(value: Optional[str]) -> Optional[str]:
    """Validate an upstream vLLM version (None stays None)."""
    if value is None:
        return None
    value = str(value).strip()
    if not _UPSTREAM_VLLM.match(value):
        raise ValueError(f"upstream_vllm {value!r} is not a vLLM version such as 0.31.0 or 0.26.0.dev+481e481be")
    return value


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
    upstream_vllm: Optional[str] = None
    kv_features: List[str] = Field(default_factory=list)
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
    #: the upstream vLLM base of a vLLM build (the planner picks its engine record by version, then by this minor)
    upstream_vllm: Optional[str] = None
    #: the KV-cache features verified on this build (``KV_FEATURES``); empty renders no KV setting
    kv_features: List[str] = Field(default_factory=list)

    @field_validator("upstream_vllm")
    @classmethod
    def _valid_upstream(cls, value: Optional[str]) -> Optional[str]:
        """Refuse what is not an upstream vLLM version."""
        return check_upstream_vllm(value)

    @field_validator("kv_features")
    @classmethod
    def _valid_features(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Refuse unknown names; deduplicate and sort the rest."""
        return check_kv_features(value)


class EngineVersionUpdate(BaseModel):
    version: Optional[str] = None
    device_architecture: Optional[DeviceArchitecture] = None
    container_image: Optional[str] = None
    #: None keeps the stored value
    upstream_vllm: Optional[str] = None
    #: None keeps the stored features; an empty list withdraws them all
    kv_features: Optional[List[str]] = None

    @field_validator("upstream_vllm")
    @classmethod
    def _valid_upstream(cls, value: Optional[str]) -> Optional[str]:
        """Refuse what is not an upstream vLLM version."""
        return check_upstream_vllm(value)

    @field_validator("kv_features")
    @classmethod
    def _valid_features(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Refuse unknown names; deduplicate and sort the rest."""
        return check_kv_features(value)


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
    supported_endpoints: Optional[Dict[str, Any]] = None
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
    supported_endpoints: Optional[Dict[str, Any]] = None


class EngineCompatibilityUpdate(BaseModel):
    architectures: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None
    supported_tool_calling_parser_types: Optional[Dict[str, Any]] = None
    supported_reasoning_parsers: Optional[Dict[str, Any]] = None
    supported_endpoints: Optional[Dict[str, Any]] = None


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
    upstream_vllm: Optional[str] = None
    kv_features: List[str] = Field(default_factory=list)
    # Parsers this engine version registers (None = no list stored, so nothing is filtered). Used to drop
    # rule and architecture parsers that an older build doesn't have; not part of the response.
    supported_tool_calling_parsers: Optional[List[str]] = Field(default=None, exclude=True)
    supported_reasoning_parsers: Optional[List[str]] = Field(default=None, exclude=True)


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
