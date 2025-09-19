from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from budmicroframe.commons.schemas import SuccessResponse
from pydantic import BaseModel


class DeviceArchitecture(Enum):
    CUDA = "CUDA"
    ROCM = "ROCM"
    CPU = "CPU"
    HPU = "HPU"


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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        """Configuration for the Engine model."""

        from_attributes = True


class EngineCompatibilityCreate(BaseModel):
    engine_version_id: UUID
    architectures: Dict[str, Any]
    features: Dict[str, Any]


class EngineCompatibilityUpdate(BaseModel):
    architectures: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None


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


class CompatibleEnginesResponse(SuccessResponse):
    compatible_engines: List[CompatibleEngine]


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
