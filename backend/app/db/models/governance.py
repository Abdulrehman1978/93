"""Reference catalogs, policy versions, lawful authority, and consent ledgers."""

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
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> Any:
    return UUID(as_uuid=True)


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str] = mapped_column(String(30), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("jurisdictions.id", ondelete="RESTRICT")
    )
    boundary_ref: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "level IN ('NATIONAL','STATE','DISTRICT','TALUKA','LOCAL')", name="jurisdictions_level"
        ),
        Index("ix_jurisdictions_parent_id", "parent_id"),
    )


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[str] = mapped_column(String(50), nullable=False)
    jurisdiction_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("jurisdictions.id", ondelete="RESTRICT")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "org_type IN ('MINISTRY','HELPLINE_OPERATOR','LEGAL_AID','HEALTH_SERVICE','EMERGENCY_DISPATCH','DISTRICT_ADMIN','SERVICE_PROVIDER')",
            name="organizations_org_type",
        ),
        Index("ix_organizations_jurisdiction_id", "jurisdiction_id"),
    )


class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version_code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "policy_type IN ('SAFETY_ESCALATION','SVI_TRIAGE','URGENCY','CONSENT_NOTICE','FOLLOW_UP','RETENTION_SCHEDULE','REFERRAL')",
            name="policy_versions_type",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="policy_versions_effective_range",
        ),
    )


class ProcessingPurpose(Base):
    __tablename__ = "processing_purposes"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    purpose_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    default_authority_code: Mapped[str | None] = mapped_column(
        String(80), ForeignKey("processing_authority_types.authority_code", ondelete="RESTRICT")
    )
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_processing_purposes_policy_version_id", "policy_version_id"),)


class ProcessingAuthorityType(Base):
    __tablename__ = "processing_authority_types"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    authority_code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    authority_source_class: Mapped[str] = mapped_column(String(50), nullable=False)
    legal_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default=text("'IN'")
    )
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "authority_source_class IN ('STATUTORY','REGULATORY','CONSTITUTIONAL','EXECUTIVE_POLICY','PRODUCT_POLICY')",
            name="processing_authority_types_authority_source_class",
        ),
        CheckConstraint(
            "status IN ('ACTIVE','SUPERSEDED','REVOKED')", name="processing_authority_types_status"
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="processing_authority_types_effective_range",
        ),
        Index("ix_processing_authority_types_jurisdiction_status", "jurisdiction", "status"),
    )


class ProcessingAuthorization(Base):
    __tablename__ = "processing_authorizations"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="RESTRICT")
    )
    interaction_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("interactions.id", ondelete="RESTRICT")
    )
    processing_purpose_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("processing_purposes.id", ondelete="RESTRICT"), nullable=False
    )
    authority_type_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("processing_authority_types.id", ondelete="RESTRICT"), nullable=False
    )
    consent_event_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("consent_events.id", ondelete="RESTRICT")
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    external_actor_reference: Mapped[str | None] = mapped_column(String(255))
    authorization_reason: Mapped[str] = mapped_column(Text, nullable=False)
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "case_id IS NOT NULL OR interaction_id IS NOT NULL",
            name="processing_authorizations_scope_required",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at >= created_at",
            name="processing_authorizations_expiry",
        ),
        Index("ix_processing_authorizations_actor_id", "actor_id"),
        Index("ix_processing_authorizations_case_id", "case_id"),
        Index("ix_processing_authorizations_interaction_id", "interaction_id"),
    )


class ConsentEvent(Base):
    __tablename__ = "consent_events"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="RESTRICT")
    )
    purpose_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("processing_purposes.id", ondelete="RESTRICT"), nullable=False
    )
    choice: Mapped[str] = mapped_column(String(30), nullable=False)
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    external_actor_reference: Mapped[str | None] = mapped_column(String(255))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    previous_event_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("consent_events.id", ondelete="RESTRICT")
    )
    reason: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "choice IN ('GRANTED','DECLINED','REVOKED','EXPIRED','SUPERSEDED')",
            name="consent_events_choice",
        ),
        CheckConstraint(
            "channel IN ('PORTAL','VOICE','TEXT','IVR','OPERATOR','SYSTEM')",
            name="consent_events_channel",
        ),
        Index("ix_consent_events_actor_id", "actor_id"),
        Index("ix_consent_events_subject_purpose_time", "subject_id", "purpose_id", "occurred_at"),
    )
