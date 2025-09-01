from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from budmicroframe.shared.psql_service import PSQLBase, TimestampMixin
from sqlalchemy import DateTime, ForeignKey, String, Uuid, func, select
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship


class GuardrailProbe(PSQLBase, TimestampMixin):
    """Guardrail probe model - represents a type of vulnerability or threat detection."""

    __tablename__ = "guardrail_probes"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    uri: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    examples: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    deprecation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    provider_id: Mapped[UUID] = mapped_column(ForeignKey("provider.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    provider: Mapped["Provider"] = relationship(back_populates="probes")
    rules: Mapped[List["GuardrailRule"]] = relationship(back_populates="probe", cascade="all, delete-orphan")

    @hybrid_property
    def guard_types(self) -> List[str]:
        """Python-side implementation: Aggregates unique guard_types from all rules."""
        if not self.rules:
            return []
        # Use a set to efficiently find unique types
        all_types = set()
        for rule in self.rules:
            if rule.guard_types:
                all_types.update(rule.guard_types)
        return sorted(all_types)  # sorted for consistent output

    @guard_types.expression
    def guard_types(cls):
        """SQL-side implementation: Generates a subquery to aggregate types."""
        # This subquery unnests all arrays, finds distinct values, and re-aggregates them.
        subquery = (
            select(func.array_agg(func.distinct(func.unnest(GuardrailRule.guard_types))))
            .where(GuardrailRule.probe_id == cls.id)
            .label("aggregated_guard_types")
        )
        return subquery.as_scalar()

    # You can apply the exact same pattern for scanner_types and modality_types
    @hybrid_property
    def scanner_types(self) -> List[str]:
        if not self.rules:
            return []
        all_types = set()
        for rule in self.rules:
            if rule.scanner_types:
                all_types.update(rule.scanner_types)
        return sorted(all_types)

    @scanner_types.expression
    def scanner_types(cls):
        subquery = (
            select(func.array_agg(func.distinct(func.unnest(GuardrailRule.scanner_types))))
            .where(GuardrailRule.probe_id == cls.id)
            .label("aggregated_scanner_types")
        )
        return subquery.as_scalar()

    @hybrid_property
    def modality_types(self) -> List[str]:
        if not self.rules:
            return []
        all_types = set()
        for rule in self.rules:
            if rule.modality_types:
                all_types.update(rule.modality_types)
        return sorted(all_types)

    @modality_types.expression
    def modality_types(cls):
        subquery = (
            select(func.array_agg(func.distinct(func.unnest(GuardrailRule.modality_types))))
            .where(GuardrailRule.probe_id == cls.id)
            .label("aggregated_modality_types")
        )
        return subquery.as_scalar()

    @hybrid_property
    def examples(self) -> List[str]:
        """Python-side implementation for examples.
        Aggregates all unique examples from rules and returns up to 10.
        """
        if not self.rules:
            return []
        all_examples = set()
        for rule in self.rules:
            if rule.examples:
                all_examples.update(rule.examples)
        # Sort for consistent output and then slice the top 10
        return sorted(all_examples)[:10]

    @examples.expression
    def examples(cls):
        """SQL expression that aggregates up to 10 unique examples into a single array."""
        # Step 1: Create a subquery to get the first 10 distinct, unnested examples for a probe.
        # We must do the LIMIT here, before the final aggregation.
        limited_examples_subquery = (
            select(func.unnest(GuardrailRule.examples).label("example"))
            .where(GuardrailRule.probe_id == cls.id)
            .distinct()
            .limit(10)
            .subquery("limited_examples")
        )

        # Step 2: Aggregate the results of the subquery back into an array.
        final_query = select(func.array_agg(limited_examples_subquery.c.example))

        return final_query.label("aggregated_examples").as_scalar()


class GuardrailRule(PSQLBase, TimestampMixin):
    """Specific rules within each probe."""

    __tablename__ = "guardrail_rules"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    probe_id: Mapped[UUID] = mapped_column(
        ForeignKey("guardrail_probes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    uri: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    examples: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    guard_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    scanner_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    modality_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    deprecation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    probe: Mapped["GuardrailProbe"] = relationship("GuardrailProbe", back_populates="rules")
