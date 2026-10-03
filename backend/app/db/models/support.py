"""Service directory, referrals, support outcomes, and follow-up history."""

from __future__ import annotations

import uuid
from datetime import datetime, time
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> Any:
    return UUID(as_uuid=True)


class ServiceResource(Base):
    __tablename__ = "service_resources"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    canonical_identifier: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    service_type: Mapped[str] = mapped_column(String(80), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("jurisdictions.id", ondelete="RESTRICT")
    )
    languages: Mapped[list[str] | None] = mapped_column(ARRAY(String(20)))
    contact_channel: Mapped[str] = mapped_column(String(30), nullable=False)
    contact_endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    availability_status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'UNKNOWN'")
    )
    capacity_status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'NOT_REPORTED'")
    )
    capacity_last_reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    freshness_status: Mapped[str] = mapped_column(
        String(25), nullable=False, server_default=text("'UNKNOWN'")
    )
    integration_status: Mapped[str] = mapped_column(
        String(25), nullable=False, server_default=text("'NOT_CONFIGURED'")
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "contact_channel IN ('PHONE','EMAIL','WEB','PORTAL','IN_PERSON','OTHER')",
            name="service_resources_contact_channel",
        ),
        CheckConstraint(
            "availability_status IN ('OPEN','LIMITED','CLOSED','UNKNOWN')",
            name="service_resources_availability_status",
        ),
        CheckConstraint(
            "capacity_status IN ('AVAILABLE','LIMITED','FULL','NOT_REPORTED')",
            name="service_resources_capacity_status",
        ),
        CheckConstraint(
            "freshness_status IN ('VERIFIED_CURRENT','STALE','UNKNOWN')",
            name="service_resources_freshness_status",
        ),
        CheckConstraint(
            "integration_status IN ('NOT_CONFIGURED','SANDBOX','ADAPTER_READY','LIVE','DEGRADED','DISABLED')",
            name="service_resources_integration_status",
        ),
        CheckConstraint("version > 0", name="service_resources_version_positive"),
        Index("ix_service_resources_lookup", "jurisdiction_id", "service_type", "freshness_status"),
    )


class ResourceVerification(Base):
    __tablename__ = "resource_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    service_resource_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("service_resources.id", ondelete="RESTRICT"), nullable=False
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    verification_method: Mapped[str] = mapped_column(String(40), nullable=False)
    verified_by_actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    external_verifier_reference: Mapped[str | None] = mapped_column(String(255))
    result: Mapped[str] = mapped_column(String(25), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint(
            "result IN ('VERIFIED_CURRENT','STALE','UNAVAILABLE','UNABLE_TO_VERIFY')",
            name="resource_verifications_result",
        ),
        Index("ix_resource_verifications_verified_by_actor_id", "verified_by_actor_id"),
        Index("ix_resource_verifications_resource_time", "service_resource_id", "verified_at"),
    )


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="RESTRICT"), nullable=False
    )
    service_type: Mapped[str] = mapped_column(String(80), nullable=False)
    service_resource_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("service_resources.id", ondelete="RESTRICT")
    )
    assigned_provider_actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    processing_authorization_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("processing_authorizations.id", ondelete="RESTRICT"), nullable=False
    )
    consent_event_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("consent_events.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'RECOMMENDED'")
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'NORMAL'")
    )
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    next_action_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('RECOMMENDED','REVIEW_REQUIRED','APPROVED','DECLINED','REFERRED','ACKNOWLEDGED','CONTACT_PENDING','CONTACTED','APPOINTMENT_SCHEDULED','SERVICE_STARTED','FOLLOW_UP_DUE','COMPLETED','UNABLE_TO_CONTACT','ESCALATED','CANCELLED')",
            name="referrals_status",
        ),
        CheckConstraint(
            "priority IN ('LOW','NORMAL','HIGH','URGENT','CRITICAL')", name="referrals_priority"
        ),
        CheckConstraint("version > 0", name="referrals_version_positive"),
        Index("ix_referrals_queue", "status", "next_action_at", "priority"),
        Index("ix_referrals_case_id", "case_id"),
        Index("ix_referrals_assigned_provider_actor_id", "assigned_provider_actor_id"),
    )


class ReferralEvent(Base):
    __tablename__ = "referral_events"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    referral_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("referrals.id", ondelete="RESTRICT"), nullable=False
    )
    previous_status: Mapped[str | None] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    external_actor_reference: Mapped[str | None] = mapped_column(String(255))
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "new_status IN ('RECOMMENDED','REVIEW_REQUIRED','APPROVED','DECLINED','REFERRED','ACKNOWLEDGED','CONTACT_PENDING','CONTACTED','APPOINTMENT_SCHEDULED','SERVICE_STARTED','FOLLOW_UP_DUE','COMPLETED','UNABLE_TO_CONTACT','ESCALATED','CANCELLED')",
            name="referral_events_new_status",
        ),
        CheckConstraint(
            "previous_status IS NULL OR previous_status IN ('RECOMMENDED','REVIEW_REQUIRED','APPROVED','DECLINED','REFERRED','ACKNOWLEDGED','CONTACT_PENDING','CONTACTED','APPOINTMENT_SCHEDULED','SERVICE_STARTED','FOLLOW_UP_DUE','COMPLETED','UNABLE_TO_CONTACT','ESCALATED','CANCELLED')",
            name="referral_events_previous_status",
        ),
        Index("ix_referral_events_actor_id", "actor_id"),
        Index("ix_referral_events_referral_time", "referral_id", "occurred_at"),
    )


class SupportOutcome(Base):
    __tablename__ = "support_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    referral_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("referrals.id", ondelete="RESTRICT"), nullable=False
    )
    outcome_stage: Mapped[str] = mapped_column(String(40), nullable=False)
    evidence_state: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'UNVERIFIED'")
    )
    provenance: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by_actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    external_verifier_reference: Mapped[str | None] = mapped_column(String(255))
    document_reference: Mapped[str | None] = mapped_column(String(500))
    notes_reference: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "outcome_stage IN ('RECOMMENDED','REFERRED','ACKNOWLEDGED','CONTACTED','SERVICE_STARTED','FOLLOW_UP_CONFIRMED','COMPLETED')",
            name="support_outcomes_outcome_stage",
        ),
        CheckConstraint(
            "evidence_state IN ('UNVERIFIED','PROVIDER_CONFIRMED','CITIZEN_CONFIRMED','DUAL_CONFIRMED','DOCUMENT_CONFIRMED','UNABLE_TO_VERIFY')",
            name="support_outcomes_evidence_state",
        ),
        Index("ix_support_outcomes_verified_by_actor_id", "verified_by_actor_id"),
        Index("ix_support_outcomes_referral_time", "referral_id", "created_at"),
    )


class FollowUpPolicy(Base):
    __tablename__ = "follow_up_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    source_class: Mapped[str] = mapped_column(String(40), nullable=False)
    service_type: Mapped[str] = mapped_column(String(80), nullable=False)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False)
    interval_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger: Mapped[str] = mapped_column(String(50), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("interval_hours > 0", name="follow_up_policies_interval_positive"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="follow_up_policies_effective_range",
        ),
        Index("ix_follow_up_policies_lookup", "service_type", "urgency", "effective_from"),
    )


class ContactAttemptPolicy(Base):
    __tablename__ = "contact_attempt_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    follow_up_policy_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("follow_up_policies.id", ondelete="RESTRICT"), nullable=False
    )
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    spacing_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    safe_callback_start: Mapped[time | None] = mapped_column(Time(timezone=False))
    safe_callback_end: Mapped[time | None] = mapped_column(Time(timezone=False))
    alternative_channel: Mapped[str | None] = mapped_column(String(30))

    __table_args__ = (
        CheckConstraint("max_attempts > 0", name="contact_attempt_policies_max_attempts_positive"),
        CheckConstraint("spacing_hours > 0", name="contact_attempt_policies_spacing_positive"),
        Index("ix_contact_attempt_policies_follow_up_policy_id", "follow_up_policy_id"),
    )


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    referral_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("referrals.id", ondelete="RESTRICT"), nullable=False
    )
    follow_up_policy_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("follow_up_policies.id", ondelete="RESTRICT"), nullable=False
    )
    contact_attempt_policy_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("contact_attempt_policies.id", ondelete="RESTRICT")
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False, server_default=text("'DUE'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('DUE','IN_PROGRESS','COMPLETED','CANCELLED','OPTED_OUT')",
            name="follow_ups_status",
        ),
        Index("ix_follow_ups_due", "status", "due_at"),
    )


class ContactAttempt(Base):
    __tablename__ = "contact_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    follow_up_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("follow_ups.id", ondelete="RESTRICT"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    outcome: Mapped[str] = mapped_column(String(30), nullable=False)
    safe_contact_check: Mapped[str] = mapped_column(String(25), nullable=False)
    policy_reference: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("contact_attempt_policies.id", ondelete="RESTRICT"), nullable=False
    )
    notes_reference: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        CheckConstraint(
            "safe_contact_check IN ('PASSED','FAILED','NOT_PERFORMED')",
            name="contact_attempts_safe_contact_check",
        ),
        Index("ix_contact_attempts_follow_up_time", "follow_up_id", "attempted_at"),
    )
