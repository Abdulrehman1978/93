"""Small, explicit database command surface for local and CI workflows."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select, text

from app.config import settings
from app.database import async_session_factory, engine
from app.db.models import (
    Jurisdiction,
    Organization,
    PolicyVersion,
    ProcessingAuthorityType,
    ProcessingPurpose,
)

ROOT = Path(__file__).resolve().parents[2]


def _run_alembic(*args: str) -> None:
    completed = subprocess.run([sys.executable, "-m", "alembic", *args], cwd=ROOT, check=False)
    raise SystemExit(completed.returncode)


async def _seed_reference_data() -> None:
    async with async_session_factory() as session:
        now = datetime.now(UTC)
        policy = await session.scalar(
            select(PolicyVersion).where(PolicyVersion.version_code == "packet-03-baseline-1")
        )
        if policy is None:
            policy = PolicyVersion(
                policy_type="CONSENT_NOTICE",
                version_code="packet-03-baseline-1",
                content_hash="packet03-reference-seed-v1",
                effective_from=now,
            )
            session.add(policy)
            await session.flush()

        if await session.scalar(select(Jurisdiction).where(Jurisdiction.code == "IN")) is None:
            session.add(Jurisdiction(code="IN", name="India", level="NATIONAL"))
        if (
            await session.scalar(select(Organization).where(Organization.code == "SAMBAL_CORE"))
            is None
        ):
            session.add(
                Organization(code="SAMBAL_CORE", name="SAMBAL Core Service", org_type="MINISTRY")
            )

        authorities = (
            ("CONSENT", "Consent event", "PRODUCT_POLICY", "Consent ledger event"),
            (
                "STATE_FUNCTION_UNDER_LAW",
                "State function under law",
                "STATUTORY",
                "Applicable public-service enabling law",
            ),
            (
                "LEGAL_OBLIGATION",
                "Legal obligation",
                "STATUTORY",
                "Applicable statutory obligation",
            ),
            (
                "MEDICAL_EMERGENCY",
                "Medical emergency",
                "STATUTORY",
                "Emergency processing authority",
            ),
            (
                "PUBLIC_ORDER_OR_DISASTER_ASSISTANCE",
                "Public order or disaster assistance",
                "STATUTORY",
                "Emergency public-order authority",
            ),
            (
                "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
                "Voluntarily provided for specified purpose",
                "PRODUCT_POLICY",
                "Specified-purpose intake",
            ),
        )
        for code, name, source_class, legal_reference in authorities:
            if (
                await session.scalar(
                    select(ProcessingAuthorityType).where(
                        ProcessingAuthorityType.authority_code == code
                    )
                )
                is None
            ):
                session.add(
                    ProcessingAuthorityType(
                        authority_code=code,
                        display_name=name,
                        source_class=source_class,
                        legal_reference=legal_reference,
                        effective_from=now,
                    )
                )

        purposes = (
            ("PURP-01", "Complaint Intake", "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE"),
            ("PURP-04", "AI-Assisted Triage", "STATE_FUNCTION_UNDER_LAW"),
            ("PURP-08", "General Support Referral", "CONSENT"),
            ("PURP-13", "Closed-Loop Follow-Up", "CONSENT"),
            ("PURP-17", "Audit and Security Logging", "LEGAL_OBLIGATION"),
        )
        for code, name, authority in purposes:
            if (
                await session.scalar(
                    select(ProcessingPurpose).where(ProcessingPurpose.purpose_code == code)
                )
                is None
            ):
                session.add(
                    ProcessingPurpose(
                        purpose_code=code,
                        name=name,
                        description="Synthetic Packet 03 reference catalog entry.",
                        default_authority_code=authority,
                        policy_version_id=policy.id,
                    )
                )
        await session.commit()


def migrate() -> None:
    _run_alembic("upgrade", "head")


def reset() -> None:
    if settings.ENVIRONMENT not in ("development", "testing"):
        raise SystemExit("Refusing db-reset outside development/testing environment")
    _run_alembic("downgrade", "base")
    _run_alembic("upgrade", "head")
    asyncio.run(_seed_reference_data())


def seed() -> None:
    asyncio.run(_seed_reference_data())


def check() -> None:
    async def _check() -> None:
        async with engine.connect() as connection:
            version = await connection.scalar(text("SELECT version()"))
            print(version)

    asyncio.run(_check())


def drift() -> None:
    _run_alembic("check")


def test() -> None:
    completed = subprocess.run([sys.executable, "-m", "pytest"], cwd=ROOT, check=False)
    raise SystemExit(completed.returncode)
