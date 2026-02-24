from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List
from uuid import uuid4

from budmicroframe.shared.psql_service import PSQLBase, TimestampMixin
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Table

from ..commons.constants import ModalityEnum, ModelEndpointEnum, ModelStatusEnum, ProviderCapabilityEnum


if TYPE_CHECKING:
    from ..engine.models import EngineVersion
    from ..guardrails.models import GuardrailProbe


class License(PSQLBase, TimestampMixin):
    """Represents license information for AI models in the system.

    This class stores comprehensive license details including the license type,
    terms, and frequently asked questions about usage rights. Each license can
    be associated with multiple models, allowing for efficient reuse of common
    license terms.

    Attributes:
        id (UUID): Unique identifier for the license.
        key (str): Unique key identifier for the license (e.g., 'apache-2.0', 'openai-api').
        name (str): Human-readable name of the license.
        type (str): Classification of the license type (e.g., 'Permissive Open Source').
        type_description (str): Detailed description of the license type.
        type_suitability (str): Suitability rating (MOST, GOOD, LOW, WORST).
        faqs (List[Dict]): JSON array of frequently asked questions with answers,
            reasons, and impact assessments.
        models (List[ModelInfo]): Relationship to models using this license.

    Note:
        The license key should be unique and is used as the primary identifier
        for referencing licenses in seeders and other parts of the system.
    """

    __tablename__ = "license"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    type_description: Mapped[str] = mapped_column(Text, nullable=False)
    type_suitability: Mapped[str] = mapped_column(String, nullable=False)
    faqs: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=False)

    models: Mapped[List["ModelInfo"]] = relationship(back_populates="license")


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
    capabilities: Mapped[List[str]] = mapped_column(ARRAY(Enum(ProviderCapabilityEnum)), nullable=True)

    models: Mapped[List["ModelInfo"]] = relationship(back_populates="provider")
    probes: Mapped[List["GuardrailProbe"]] = relationship(back_populates="provider")
    supported_versions: Mapped[List["EngineVersion"]] = relationship(
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
    license_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("license.id"), nullable=True)
    model_architecture_class_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("model_architecture_class.id"), nullable=True
    )
    chat_template: Mapped[str] = mapped_column(Text, nullable=True)
    tool_calling_parser_type: Mapped[str] = mapped_column(String, nullable=True)
    reasoning_parser_type: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[ModelStatusEnum] = mapped_column(
        Enum(ModelStatusEnum), nullable=False, default=ModelStatusEnum.ACTIVE
    )

    provider: Mapped[Provider] = relationship(back_populates="models")
    license: Mapped[License] = relationship(back_populates="models")
    details: Mapped["ModelDetails"] = relationship(back_populates="model_info", uselist=False)
    capabilities: Mapped[List["ModelCapability"]] = relationship(back_populates="model_info")
    architecture_class: Mapped["ModelArchitectureClass"] = relationship(back_populates="models")


class ModelArchitectureClass(PSQLBase, TimestampMixin):
    """Maps model architecture classes to their families and capabilities.

    This table stores the mapping between specific model architecture classes
    (e.g., 'LlamaForCausalLM') and their family names, along with their
    tool calling, reasoning, LoRA, and parallelism capabilities.

    Attributes:
        id (UUID): Unique identifier for the architecture class.
        class_name (str): The model architecture class name (e.g., 'LlamaForCausalLM').
        architecture_family (str): The family this architecture belongs to (e.g., 'llama').
        tool_calling_parser_type (str): The tool calling parser type if supported.
        reasoning_parser_type (str): The reasoning parser type if supported.
        supports_lora (bool): Whether this architecture supports LoRA fine-tuning.
        supports_pipeline_parallelism (bool): Whether this architecture supports pipeline parallelism.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """

    __tablename__ = "model_architecture_class"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    class_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    architecture_family: Mapped[str] = mapped_column(String, nullable=False)
    tool_calling_parser_type: Mapped[str] = mapped_column(String, nullable=True)
    reasoning_parser_type: Mapped[str] = mapped_column(String, nullable=True)
    supports_lora: Mapped[bool] = mapped_column(nullable=False, default=False)
    supports_pipeline_parallelism: Mapped[bool] = mapped_column(nullable=False, default=False)

    models: Mapped[List["ModelInfo"]] = relationship(back_populates="architecture_class")


class ModelCapability(PSQLBase, TimestampMixin):
    """Stores model capabilities for specific model-engine version combinations.

    This table tracks which capabilities (tool calling, reasoning) are supported
    for specific models when used with specific engine versions.

    Attributes:
        id (UUID): Unique identifier for the capability record.
        model_info_id (UUID): Foreign key to the model_info table.
        engine_version_id (UUID): Foreign key to the engine_version table.
        tool_calling_enabled (bool): Whether tool calling is enabled.
        tool_calling_template (str): The specific tool calling template to use.
        reasoning_parser_enabled (bool): Whether reasoning parser is enabled.
        reasoning_parser_type (str): The specific reasoning parser type to use.
        compatibility_notes (Dict): Additional compatibility information.
        model_info (ModelInfo): Relationship to the associated model.
        engine_version (EngineVersion): Relationship to the associated engine version.
    """

    __tablename__ = "model_capability"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    model_info_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("model_info.id"), nullable=False)
    engine_version_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("engine_version.id"), nullable=False)
    tool_calling_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    tool_calling_parser_type: Mapped[str] = mapped_column(String, nullable=True)
    reasoning_parser_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    reasoning_parser_type: Mapped[str] = mapped_column(String, nullable=True)
    compatibility_notes: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)

    model_info: Mapped[ModelInfo] = relationship("ModelInfo", back_populates="capabilities")
    engine_version: Mapped["EngineVersion"] = relationship("EngineVersion", back_populates="model_capabilities")


class ModelDetails(PSQLBase, TimestampMixin):
    """Stores enriched details about AI models extracted from documentation.

    This class contains detailed information about models including descriptions,
    use cases, evaluations, and other metadata extracted from model documentation.

    Attributes:
        id (UUID): Unique identifier for the model details.
        model_info_id (UUID): Foreign key reference to the associated ModelInfo.
        description (str): Comprehensive description of the model.
        advantages (List[str]): List of model strengths and capabilities.
        disadvantages (List[str]): List of model limitations and weaknesses.
        use_cases (List[str]): List of practical applications for the model.
        evaluations (List[Dict]): Model evaluation scores and benchmarks.
        languages (List[str]): Supported languages.
        tags (List[str]): Categorization tags for the model.
        tasks (List[str]): Supported tasks and capabilities.
        papers (List[Dict]): Related research papers and publications.
        github_url (str): GitHub repository URL if available.
        website_url (str): Model website URL if available.
        logo_url (str): Model logo URL if available.
        architecture (Dict): Technical architecture details.
        model_tree (Dict): Information about model derivatives and relationships.
        extraction_metadata (Dict): Metadata about when and how the data was extracted.
        model_info (ModelInfo): Relationship to the associated ModelInfo.
    """

    __tablename__ = "model_details"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    model_info_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("model_info.id"), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    advantages: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    disadvantages: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    use_cases: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    evaluations: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    languages: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    tasks: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    papers: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    github_url: Mapped[str] = mapped_column(String, nullable=True)
    website_url: Mapped[str] = mapped_column(String, nullable=True)
    logo_url: Mapped[str] = mapped_column(String, nullable=True)
    architecture: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    model_tree: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    extraction_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)

    model_info: Mapped[ModelInfo] = relationship(back_populates="details")


# Engine Version Provider Association
engine_version_provider = Table(
    "engine_version_provider",
    PSQLBase.metadata,
    Column("engine_version_id", UUID, ForeignKey("engine_version.id"), primary_key=True),
    Column("provider_id", UUID, ForeignKey("provider.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    ),
)

# Engine Version Model Info Association
engine_version_model_info = Table(
    "engine_version_model_info",
    PSQLBase.metadata,
    Column("engine_version_id", UUID, ForeignKey("engine_version.id"), primary_key=True),
    Column("model_info_id", UUID, ForeignKey("model_info.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    ),
)
