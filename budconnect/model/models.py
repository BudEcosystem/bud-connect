from datetime import UTC, datetime
from typing import Any, Dict, List
from uuid import uuid4

from budmicroframe.shared.psql_service import PSQLBase, TimestampMixin
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Table

from ..commons.constants import ModalityEnum, ModelEndpointEnum


class Provider(PSQLBase, TimestampMixin):
    """Represents an AI model provider organization or service in the system.

    This class stores information about entities that provide AI models, such as
    OpenAI, Anthropic, Google, or custom providers. Each provider can offer multiple
    models of different types and capabilities.

    Attributes:
        id (UUID): Unique identifier for the provider.
        name (str): The name of the provider (e.g., "OpenAI", "Anthropic").
        provider_type (str): Classification of the provider type, such as "cloud",
            "open_source", "proprietary", "custom", etc., which helps categorize
            and filter providers based on their characteristics.
        models (List[ModelInfo]): Relationship to the collection of models offered
            by this provider. This represents a one-to-many relationship where a
            provider can have multiple models.

    Note:
        When creating a new provider, both name and provider_type are required fields.
        The combination of these fields can be used for identifying specific provider
        implementations in the application logic.
    """

    __tablename__ = "provider"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    provider_type: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    icon: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    credentials: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=False)

    models: Mapped[List["ModelInfo"]] = relationship(back_populates="provider")
    supported_versions: Mapped[List["EngineVersion"]] = relationship(  # noqa: F821
        "EngineVersion", secondary="engine_version_provider", back_populates="supported_providers"
    )


class ModelInfo(PSQLBase, TimestampMixin):
    """Represents information about an AI model in the system.

    This class stores metadata about AI models, including their URI, modality type,
    configuration parameters, and associated provider information.

    Attributes:
        id (UUID): Unique identifier for the model.
        uri (str): Uniform Resource Identifier for accessing the model.
        modality (ModalityEnum): The type of modality this model supports (e.g., LLM, IMAGE).
            Can be null if the model doesn't fit into a specific modality category.
        config (Dict[str, Any]): JSON configuration containing model-specific parameters
            such as token limits, pricing information, and capabilities.
        provider_id (UUID): Foreign key reference to the provider that offers this model.
        provider (Provider): Relationship to the provider entity that owns or serves this model.

    Note:
        The config field can store various model-specific details like maximum token limits,
        pricing information, supported features, and other technical specifications.
    """

    __tablename__ = "model_info"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    uri: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    modality: Mapped[List[ModalityEnum]] = mapped_column(ARRAY(Enum(ModalityEnum)), nullable=True)
    input_cost: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    output_cost: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    cache_cost: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    search_context_cost_per_query: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    tokens: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    rate_limits: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    media_limits: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    features: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    provider_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("provider.id"), nullable=False)
    deprecation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    endpoints: Mapped[List[ModelEndpointEnum]] = mapped_column(ARRAY(Enum(ModelEndpointEnum)), nullable=True)

    provider: Mapped[Provider] = relationship(back_populates="models")


# Engine Version Provider Association
engine_version_provider = Table(
    "engine_version_provider",
    PSQLBase.metadata,
    Column("engine_version_id", UUID, ForeignKey("engine_version.id"), primary_key=True),
    Column("provider_id", UUID, ForeignKey("provider.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    ),
)

# Engine Version Model Info Association
engine_version_model_info = Table(
    "engine_version_model_info",
    PSQLBase.metadata,
    Column("engine_version_id", UUID, ForeignKey("engine_version.id"), primary_key=True),
    Column("model_info_id", UUID, ForeignKey("model_info.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    ),
)
