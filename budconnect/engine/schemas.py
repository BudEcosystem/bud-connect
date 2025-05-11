from enum import Enum
from typing import List

from budmicroframe.commons.schemas import SuccessResponse
from pydantic import BaseModel


class DeviceArchitecture(Enum):
    CUDA = "cuda"
    ROCM = "rocm"
    CPU = "cpu"
    HPU = "hpu"


class Engine(BaseModel):
    name: str


class EngineVersion(BaseModel):
    version: str
    device_architecture: DeviceArchitecture
    container_image: str
    engine_id: str


class ModelArchitecture(BaseModel):
    name: str


class Feature(BaseModel):
    name: str


class EngineCompatibility(BaseModel):
    engine_version_id: str
    architectures: List[ModelArchitecture]
    features: List[Feature]


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
