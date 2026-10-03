"""Independent assessment dimensions, provenance, evidence pointers, and review ledger."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> Any:
    return UUID(as_uuid=True)


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="RESTRICT"), nullable=False
    )
    interaction_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("interactions.id", ondelete="RESTRICT")
    )
    assessment_type: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'TRIAGE'")
    )
    status: Mapped[str] = mapped_column(
        String(25), nullable=False, server_default=text("'ADVISORY'")
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "assessment_type IN ('TRIAGE','RECALCULATION','HUMAN_REVIEW')", name="assessments_type"
        ),
        CheckConstraint(
            "status IN ('ADVISORY','UNDER_REVIEW','FINALIZED','DISMISSED')",
            name="assessments_status",
        ),
        CheckConstraint("version_number > 0", name="assessments_version_positive"),
        Index("ix_assessments_case_created", "case_id", "created_at"),
        Index("ix_assessments_interaction_id", "interaction_id"),
    )


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    task: Mapped[str] = mapped_column(String(80), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(150), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(100))
    input_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    failure_class: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('STARTED','SUCCEEDED','FAILED','CANCELLED')", name="model_runs_status"
        ),
        CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0", name="model_runs_latency_nonnegative"
        ),
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at", name="model_runs_time_range"
        ),
    )


class ImmediateSafetyResult(Base):
    __tablename__ = "immediate_safety_results"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("assessments.id", ondelete="RESTRICT"), nullable=False
    )
    state: Mapped[str] = mapped_column(String(35), nullable=False)
    confidence: Mapped[float | None] = mapped_column()
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    model_run_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("model_runs.id", ondelete="RESTRICT")
    )
    uncertainty: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "state IN ('NO_IMMEDIATE_SIGNAL','REVIEW_RECOMMENDED','ELEVATED','CRITICAL_REVIEW','INSUFFICIENT_INFORMATION')",
            name="immediate_safety_results_state",
        ),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="immediate_safety_results_confidence",
        ),
        Index("ix_immediate_safety_results_assessment_id", "assessment_id"),
    )


class SviResult(Base):
    __tablename__ = "svi_results"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("assessments.id", ondelete="RESTRICT"), nullable=False
    )
    band: Mapped[str | None] = mapped_column(String(20))
    numeric_score: Mapped[float | None] = mapped_column()
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    model_run_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("model_runs.id", ondelete="RESTRICT")
    )
    uncertainty: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "band IS NULL OR band IN ('LOW','MODERATE','HIGH','CRITICAL')", name="svi_results_band"
        ),
        CheckConstraint(
            "numeric_score IS NULL OR numeric_score >= 0", name="svi_results_numeric_score"
        ),
        Index("ix_svi_results_assessment_id", "assessment_id"),
    )


class IncidentUrgencyResult(Base):
    __tablename__ = "incident_urgency_results"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("assessments.id", ondelete="RESTRICT"), nullable=False
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float | None] = mapped_column()
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    model_run_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("model_runs.id", ondelete="RESTRICT")
    )
    uncertainty: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "level IN ('ROUTINE','PRIORITY','URGENT','CRITICAL')",
            name="incident_urgency_results_level",
        ),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="incident_urgency_results_confidence",
        ),
        Index("ix_incident_urgency_results_assessment_id", "assessment_id"),
    )


class AssessmentEvidence(Base):
    __tablename__ = "assessment_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("assessments.id", ondelete="RESTRICT"), nullable=False
    )
    modality: Mapped[str] = mapped_column(String(30), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    source_start: Mapped[int | None] = mapped_column(Integer)
    source_end: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column()
    quality: Mapped[float | None] = mapped_column()
    provider: Mapped[str | None] = mapped_column(String(100))
    model_identifier: Mapped[str | None] = mapped_column(String(150))
    provenance: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    uncertainty: Mapped[str | None] = mapped_column(Text)
    human_review_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'NOT_REVIEWED'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "source_start IS NULL OR source_start >= 0", name="assessment_evidence_source_start"
        ),
        CheckConstraint(
            "source_end IS NULL OR source_end >= 0", name="assessment_evidence_source_end"
        ),
        CheckConstraint(
            "source_end IS NULL OR source_start IS NULL OR source_end >= source_start",
            name="assessment_evidence_source_range",
        ),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="assessment_evidence_confidence",
        ),
        CheckConstraint(
            "quality IS NULL OR quality BETWEEN 0 AND 1", name="assessment_evidence_quality"
        ),
        CheckConstraint(
            "human_review_status IN ('NOT_REVIEWED','REVIEWED','DISMISSED')",
            name="assessment_evidence_review_status",
        ),
        Index("ix_assessment_evidence_assessment_id", "assessment_id"),
    )


class AssessmentReview(Base):
    __tablename__ = "assessment_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("assessments.id", ondelete="RESTRICT"), nullable=False
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    external_actor_reference: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    previous_output_reference: Mapped[str | None] = mapped_column(String(500))
    replacement_reference: Mapped[str | None] = mapped_column(String(500))
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "action IN ('ACCEPT','MODIFY','DISMISS','ESCALATE','REQUEST_SUPERVISOR','CORRECT_TRANSCRIPT','CORRECT_FACT','FLAG_AI_ERROR')",
            name="assessment_reviews_action",
        ),
        Index("ix_assessment_reviews_actor_id", "actor_id"),
        Index("ix_assessment_reviews_assessment_time", "assessment_id", "created_at"),
    )
