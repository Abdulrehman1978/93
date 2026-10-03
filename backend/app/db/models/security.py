"""Authoritative actors, scoped roles, identity mappings, and short-lived elevation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> Any:
    return UUID(as_uuid=True)


class Actor(Base):
    """Minimal local authorization subject; IdP profile data stays external."""

    __tablename__ = "actors"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    actor_type: Mapped[str] = mapped_column(String(30), nullable=False)
    display_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ACTIVE'"))
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    jurisdiction_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("jurisdictions.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('STAFF','SERVICE_PROVIDER','CITIZEN','SYSTEM','AUDITOR')",
            name="actors_type",
        ),
        CheckConstraint("status IN ('ACTIVE','SUSPENDED','DISABLED')", name="actors_status"),
        Index("ix_actors_scope", "organization_id", "jurisdiction_id", "status"),
    )


class ActorIdentity(Base):
    """Maps an external issuer/sub pair to one internal actor."""

    __tablename__ = "actor_identities"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT"), nullable=False
    )
    provider_code: Mapped[str] = mapped_column(String(80), nullable=False)
    issuer: Mapped[str] = mapped_column(String(500), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ACTIVE'"))

    __table_args__ = (
        UniqueConstraint("issuer", "subject", name="uq_actor_identities_issuer_subject"),
        CheckConstraint("status IN ('ACTIVE','REVOKED')", name="actor_identities_status"),
        Index("ix_actor_identities_actor_id", "actor_id"),
        Index("ix_actor_identities_provider_subject", "provider_code", "subject"),
    )


class Role(Base):
    """Small role catalog; permission membership is a versioned code registry."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (CheckConstraint("status IN ('ACTIVE','DISABLED')", name="roles_status"),)


class ActorRoleBinding(Base):
    """Time-bounded role assignment with organization/jurisdiction scope."""

    __tablename__ = "actor_role_bindings"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("organizations.id", ondelete="RESTRICT")
    )
    jurisdiction_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("jurisdictions.id", ondelete="RESTRICT")
    )
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    granted_by_actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("policy_versions.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="actor_role_bindings_effective_range",
        ),
        CheckConstraint(
            "granted_by_actor_id IS NULL OR granted_by_actor_id <> actor_id",
            name="actor_role_bindings_no_self_grant",
        ),
        Index("ix_actor_role_bindings_active", "actor_id", "effective_from", "effective_to"),
        Index(
            "ix_actor_role_bindings_scope",
            "organization_id",
            "jurisdiction_id",
            "role_id",
        ),
    )


class AccessElevation(Base):
    """Short-lived, scoped, human-approved exceptional access."""

    __tablename__ = "access_elevations"

    id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), primary_key=True, server_default=text("gen_random_uuid()")
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT"), nullable=False
    )
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(255))
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("cases.id", ondelete="RESTRICT")
    )
    requested_permission: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    policy_source: Mapped[str] = mapped_column(String(80), nullable=False)
    approved_by_actor_id: Mapped[uuid.UUID | None] = mapped_column(
        _uuid(), ForeignKey("actors.id", ondelete="RESTRICT")
    )
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ACTIVE'"))
    correlation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "case_id IS NOT NULL OR resource_id IS NOT NULL",
            name="access_elevations_scope_required",
        ),
        CheckConstraint("expires_at > effective_from", name="access_elevations_expiry"),
        CheckConstraint(
            "status IN ('ACTIVE','EXPIRED','REVOKED')", name="access_elevations_status"
        ),
        CheckConstraint(
            "approved_by_actor_id IS NULL OR approved_by_actor_id <> actor_id",
            name="access_elevations_no_self_approval",
        ),
        Index("ix_access_elevations_active", "actor_id", "status", "expires_at"),
        Index("ix_access_elevations_case_id", "case_id"),
    )
