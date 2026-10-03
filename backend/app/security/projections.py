"""Explicit minimum-data DTOs; protected routes never serialize ORM objects."""

from __future__ import annotations

import uuid

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Case, Referral


class CaseSummaryView(BaseModel):
    case_id: uuid.UUID
    public_tracking_id: str
    status: str
    priority: str


class ProviderReferralView(BaseModel):
    referral_id: uuid.UUID
    service_type: str
    status: str
    priority: str
    next_action_at: str | None


class DataProjectionService:
    """Builds recipient-specific views after authorization has already passed."""

    async def case_summary(
        self, session: AsyncSession, case_id: uuid.UUID
    ) -> CaseSummaryView | None:
        row = (
            await session.execute(
                select(Case.id, Case.public_tracking_id, Case.status, Case.priority).where(
                    Case.id == case_id
                )
            )
        ).one_or_none()
        if row is None:
            return None
        return CaseSummaryView(
            case_id=row.id,
            public_tracking_id=row.public_tracking_id,
            status=row.status,
            priority=row.priority,
        )

    async def provider_referral(
        self, session: AsyncSession, referral_id: uuid.UUID
    ) -> ProviderReferralView | None:
        row = (
            await session.execute(
                select(
                    Referral.id,
                    Referral.service_type,
                    Referral.status,
                    Referral.priority,
                    Referral.next_action_at,
                ).where(Referral.id == referral_id)
            )
        ).one_or_none()
        if row is None:
            return None
        return ProviderReferralView(
            referral_id=row.id,
            service_type=row.service_type,
            status=row.status,
            priority=row.priority,
            next_action_at=row.next_action_at.isoformat() if row.next_action_at else None,
        )
