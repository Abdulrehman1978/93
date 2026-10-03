"""Subjects, administrative cases, interactions, and source-language content."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
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


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    subject_reference: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    classification: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'IDENTIFIABLE'")
    )
    synthetic_marker: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "classification IN ('IDENTIFIABLE','PSEUDONYMIZED','DE_IDENTIFIED','ANONYMIZED_VALIDATED','SYNTHETIC')",
            name="subjects_classification",
        ),
        CheckConstraint(
            "synthetic_marker IS NULL OR synthetic_marker = 'SYNTHETIC_DEMO'",
            name="subjects_synthetic_marker",
        ),
    )


class SubjectContact(Base):
    __tablename__ = "subject_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_value: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    safe_to_use: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "channel IN ('PHONE','EMAIL','POSTAL','OTHER')", name="subject_contacts_channel"
        ),
        Index("ix_subject_contacts_subject_id", "subject_id"),
    )


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    public_tracking_id: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    subject_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    jurisdiction_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("jurisdictions.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'OPEN'"))
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'NORMAL'")
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('OPEN','UNDER_REVIEW','REFERRED','ON_HOLD','CLOSED','CANCELLED')",
            name="cases_status",
        ),
        CheckConstraint(
            "priority IN ('LOW','NORMAL','HIGH','URGENT','CRITICAL')", name="cases_priority"
        ),
        CheckConstraint("version > 0", name="cases_version_positive"),
        CheckConstraint("closed_at IS NULL OR closed_at >= opened_at", name="cases_closed_at"),
        Index("ix_cases_queue", "status", "priority", "created_at"),
        Index("ix_cases_subject_id", "subject_id"),
        Index("ix_cases_jurisdiction_id", "jurisdiction_id"),
    )


class CaseParticipant(Base):
    __tablename__ = "case_participants"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    participant_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    participant_type: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "participant_type IN ('SUBJECT','OPERATOR','SUPERVISOR','PROVIDER','OTHER')",
            name="case_participants_type",
        ),
        Index("ix_case_participants_case_id", "case_id"),
    )


class CaseStatusEvent(Base):
    __tablename__ = "case_status_events"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="RESTRICT"), nullable=False
    )
    previous_status: Mapped[str | None] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    actor_reference: Mapped[str | None] = mapped_column(String(255))
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    policy_source: Mapped[str | None] = mapped_column(String(255))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "new_status IN ('OPEN','UNDER_REVIEW','REFERRED','ON_HOLD','CLOSED','CANCELLED')",
            name="case_status_events_new_status",
        ),
        CheckConstraint(
            "previous_status IS NULL OR previous_status IN ('OPEN','UNDER_REVIEW','REFERRED','ON_HOLD','CLOSED','CANCELLED')",
            name="case_status_events_previous_status",
        ),
        Index("ix_case_status_events_case_time", "case_id", "occurred_at"),
    )


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="RESTRICT"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'OPEN'"))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    language: Mapped[str | None] = mapped_column(String(20))
    external_reference: Mapped[str | None] = mapped_column(String(255))
    channel_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "channel IN ('VOICE','TEXT','SILENT','IVR','CHATBOT','PORTAL','MOBILE')",
            name="interactions_channel",
        ),
        CheckConstraint(
            "status IN ('OPEN','COMPLETED','ABANDONED','FAILED')", name="interactions_status"
        ),
        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at", name="interactions_time_range"
        ),
        Index("ix_interactions_case_started", "case_id", "started_at"),
    )


class InteractionEvent(Base):
    __tablename__ = "interaction_events"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    interaction_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source_reference: Mapped[str | None] = mapped_column(String(255))
    event_metadata: Mapped[dict[str, object] | None] = mapped_column("metadata", JSONB)

    __table_args__ = (
        Index("ix_interaction_events_interaction_time", "interaction_id", "occurred_at"),
    )


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    interaction_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    start_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    end_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column()
    provider: Mapped[str | None] = mapped_column(String(100))
    provider_version: Mapped[str | None] = mapped_column(String(100))
    is_final: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("sequence >= 0", name="transcript_segments_sequence_nonnegative"),
        CheckConstraint("start_ms >= 0 AND end_ms >= start_ms", name="transcript_segments_offsets"),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="transcript_segments_confidence",
        ),
        Index(
            "uq_transcript_segments_interaction_sequence", "interaction_id", "sequence", unique=True
        ),
    )


class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    transcript_segment_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("transcript_segments.id", ondelete="CASCADE"), nullable=False
    )
    target_language: Mapped[str] = mapped_column(String(20), nullable=False)
    translated_content: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(100))
    provider_version: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[float | None] = mapped_column()
    human_review_state: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'NOT_REVIEWED'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1", name="translations_confidence"
        ),
        CheckConstraint(
            "human_review_state IN ('NOT_REVIEWED','REVIEWED','CORRECTED')",
            name="translations_review_state",
        ),
        Index("ix_translations_source_language", "transcript_segment_id", "target_language"),
    )
