from typing import Any, Dict, List, Optional
from uuid import uuid4

from budmicroframe.commons import logging
from budmicroframe.shared.psql_service import PSQLBase, TimestampMixin
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from budconnect.engine.schemas import DeviceArchitecture, ParserMatchType
from budconnect.model.models import engine_version_provider


logger = logging.get_logger(__name__)


class Engine(PSQLBase, TimestampMixin):
    """Represents an engine in the system. An engine is a core component that can have multiple versions.

    Attributes:
        id: Unique identifier for the engine
        name: Name of the engine
        versions: List of versions associated with this engine.
        parser_rules: List of parser rules associated with this engine.
    """

    __tablename__ = "engine"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    versions: Mapped[List["EngineVersion"]] = relationship("EngineVersion", back_populates="engine")
    parser_rules: Mapped[List["EngineToolParserRule"]] = relationship(
        "EngineToolParserRule",
        back_populates="engine",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return a string representation of the Engine object.

        Returns:
            str: A string containing the object's class name and key attributes.
        """
        return f"<Engine(id={self.id}, name={self.name})>"


class EngineVersion(PSQLBase, TimestampMixin):
    """Represents a specific version of an engine.

    Each version is associated with a parent engine and can have compatibility specifications.

    Attributes:
        id: Unique identifier for the engine version
        engine_id: Foreign key reference to the parent engine
        version: Version string identifier
        container_image: Container image path or reference
        device_architecture: Architecture this version is built for
        engine: Relationship to the parent engine
        compatibilities: Relationship to compatibility specifications
    """

    __tablename__ = "engine_version"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    engine_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("engine.id"), nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    container_image: Mapped[str] = mapped_column(String, nullable=False)
    device_architecture: Mapped[DeviceArchitecture] = mapped_column(Enum(DeviceArchitecture), nullable=False)

    engine = relationship("Engine", back_populates="versions")
    compatibilities = relationship("EngineCompatibility", back_populates="engine_version")
    supported_providers: Mapped[List["Provider"]] = relationship(  # noqa: F821
        "Provider",
        secondary=engine_version_provider,
        back_populates="supported_versions",
        cascade="all, delete",
    )
    model_capabilities: Mapped[List["ModelCapability"]] = relationship(  # noqa: F821
        "ModelCapability", back_populates="engine_version"
    )

    def __repr__(self) -> str:
        """Return a string representation of the EngineVersion object.

        Returns:
            str: A string containing the object's class name and key attributes.
        """
        return f"<EngineVersion(id={self.id}, engine_id={self.engine_id}, version={self.version})>"


class EngineCompatibility(PSQLBase, TimestampMixin):
    """Represents compatibility specifications for an engine version.

    Defines which architectures and features are compatible with a specific engine version.

    Attributes:
        id: Unique identifier for the compatibility specification
        engine_version_id: Foreign key reference to the associated engine version
        architectures: JSON data specifying compatible architectures
        features: JSON data specifying compatible features
        engine_version: Relationship to the associated engine version
    """

    __tablename__ = "engine_compatibility"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    engine_version_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("engine_version.id"), nullable=False, unique=True)
    architectures: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    features: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    supported_tool_calling_parser_types: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)
    supported_reasoning_parsers: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)

    engine_version = relationship("EngineVersion", back_populates="compatibilities", uselist=False)

    def __repr__(self) -> str:
        """Return a string representation of the EngineCompatibility object."""
        return f"<EngineCompatibility(id={self.id}, engine_version_id={self.engine_version_id})>"


class EngineToolParserRule(PSQLBase, TimestampMixin):
    """Rule for selecting a tool parser based on model metadata for a specific engine."""

    __tablename__ = "engine_tool_parser_rule"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    engine_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("engine.id"), nullable=False)
    parser_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    match_type: Mapped[ParserMatchType] = mapped_column(
        Enum(
            ParserMatchType,
            name="engine_tool_parser_match_type",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    pattern: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    chat_template: Mapped[str] = mapped_column(Text, nullable=True)

    engine: Mapped["Engine"] = relationship("Engine", back_populates="parser_rules")

    def __repr__(self) -> str:
        """Return string representation of EngineToolParserRule."""
        return (
            f"<EngineToolParserRule(id={self.id}, engine_id={self.engine_id}, "
            f"parser_type={self.parser_type}, match_type={self.match_type}, pattern={self.pattern})>"
        )
