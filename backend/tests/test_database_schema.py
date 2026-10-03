"""PostgreSQL integration and privacy-regression tests for Packet 03."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import engine

pytestmark = pytest.mark.integration


@pytest.fixture
async def db_connection() -> AsyncIterator[AsyncConnection]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()
            await engine.dispose()


async def _case_and_interaction(connection: AsyncConnection) -> tuple[str, str]:
    subject_id = (
        await connection.execute(
            text(
                "INSERT INTO subjects (subject_reference) VALUES ('SYNTHETIC_TEST_SUBJECT') RETURNING id"
            )
        )
    ).scalar_one()
    case_id = (
        await connection.execute(
            text(
                "INSERT INTO cases (public_tracking_id, subject_id) VALUES ('TEST-TRACK-001', :subject_id) RETURNING id"
            ),
            {"subject_id": subject_id},
        )
    ).scalar_one()
    interaction_id = (
        await connection.execute(
            text(
                "INSERT INTO interactions (case_id, channel) VALUES (:case_id, 'TEXT') RETURNING id"
            ),
            {"case_id": case_id},
        )
    ).scalar_one()
    return str(case_id), str(interaction_id)


async def test_fresh_schema_is_within_budget_and_privacy_guardrails(
    db_connection: AsyncConnection,
) -> None:
    table_count = await db_connection.scalar(
        text(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name <> 'alembic_version'"
        )
    )
    assert table_count == 36
    assert table_count <= 45

    forbidden_columns = await db_connection.scalars(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND column_name IN "
            "('raw_audio_url','audio_file_path','recording_blob','voiceprint','credibility_score','lie_score','caste_inferred')"
        )
    )
    assert list(forbidden_columns) == []

    evidence_columns = set(
        await db_connection.scalars(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'assessment_evidence'"
            )
        )
    )
    assert {"raw_snippet", "full_transcript_copy", "citizen_narrative_copy"}.isdisjoint(
        evidence_columns
    )
    assert "source_reference" in evidence_columns
    assert await db_connection.scalar(
        text(
            "SELECT is_nullable = 'NO' FROM information_schema.columns "
            "WHERE table_name = 'assessment_evidence' AND column_name = 'source_reference'"
        )
    )

    assert await db_connection.scalar(
        text("SELECT to_regclass('public.processing_authorizations') IS NOT NULL")
    )
    assert await db_connection.scalar(
        text("SELECT to_regclass('public.consent_events') IS NOT NULL")
    )


async def test_foreign_keys_and_check_constraints_are_real(db_connection: AsyncConnection) -> None:
    with pytest.raises(IntegrityError):
        async with db_connection.begin_nested():
            await db_connection.execute(
                text(
                    "INSERT INTO interactions (case_id, channel) VALUES ('00000000-0000-0000-0000-000000000001', 'TEXT')"
                )
            )

    subject_id = (
        await db_connection.execute(
            text(
                "INSERT INTO subjects (subject_reference) VALUES ('SYNTHETIC_CHECK_SUBJECT') RETURNING id"
            )
        )
    ).scalar_one()
    case_id, interaction_id = await _case_and_interaction(db_connection)
    assert subject_id is not None and case_id and interaction_id
    with pytest.raises(IntegrityError):
        async with db_connection.begin_nested():
            await db_connection.execute(
                text(
                    "INSERT INTO transcript_segments "
                    "(interaction_id, sequence, start_ms, end_ms, language, content, confidence) "
                    "VALUES (:interaction_id, 0, 10, 5, 'en', 'synthetic', 1.2)"
                ),
                {"interaction_id": interaction_id},
            )


async def test_case_referral_and_assessment_dimensions_remain_independent(
    db_connection: AsyncConnection,
) -> None:
    tables: dict[str, set[str]] = {}
    for table_name, column_name in (
        await db_connection.execute(
            text(
                "SELECT table_name, column_name FROM information_schema.columns "
                "WHERE table_name IN ('cases','referrals','immediate_safety_results','svi_results','incident_urgency_results')"
            )
        )
    ).all():
        tables.setdefault(table_name, set()).add(column_name)
    assert {"status", "priority", "version"}.issubset(tables["cases"])
    assert {"status", "priority", "processing_authorization_id"}.issubset(tables["referrals"])
    assert "case_id" in tables["referrals"]
    assert {"state", "confidence", "policy_version_id"}.issubset(tables["immediate_safety_results"])
    assert {"band", "numeric_score", "policy_version_id"}.issubset(tables["svi_results"])
    assert {"level", "confidence", "policy_version_id"}.issubset(tables["incident_urgency_results"])

    all_assessment_columns = set(
        await db_connection.scalars(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name IN ('assessments','assessment_evidence','svi_results')"
            )
        )
    )
    assert not any(
        "weight" in column or "delta" in column or column == "risk_score"
        for column in all_assessment_columns
    )
    assert await db_connection.scalar(
        text(
            "SELECT is_nullable = 'YES' FROM information_schema.columns WHERE table_name = 'svi_results' AND column_name = 'numeric_score'"
        )
    )


async def test_resource_outcome_policy_and_queue_dimensions_are_separate(
    db_connection: AsyncConnection,
) -> None:
    resource_columns = set(
        await db_connection.scalars(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'service_resources'"
            )
        )
    )
    assert {
        "freshness_status",
        "availability_status",
        "capacity_status",
        "integration_status",
    }.issubset(resource_columns)
    outcome_columns = set(
        await db_connection.scalars(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'support_outcomes'"
            )
        )
    )
    assert {"evidence_state", "verified_at", "verified_by", "provenance"}.issubset(outcome_columns)
    policy_columns = set(
        await db_connection.scalars(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'follow_up_policies'"
            )
        )
    )
    assert {"policy_version_id", "effective_from", "effective_to", "interval_hours"}.issubset(
        policy_columns
    )
    job_columns = set(
        await db_connection.scalars(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'async_jobs'"
            )
        )
    )
    assert {"status", "available_at", "locked_at", "attempts", "max_attempts"}.issubset(job_columns)


async def test_append_only_history_and_audit_protection(db_connection: AsyncConnection) -> None:
    case_id, _ = await _case_and_interaction(db_connection)
    event_id = (
        await db_connection.execute(
            text(
                "INSERT INTO case_status_events (case_id, new_status, reason) "
                "VALUES (:case_id, 'OPEN', 'synthetic test') RETURNING id"
            ),
            {"case_id": case_id},
        )
    ).scalar_one()
    with pytest.raises(DBAPIError):
        async with db_connection.begin_nested():
            await db_connection.execute(
                text("UPDATE case_status_events SET reason = 'tampered' WHERE id = :event_id"),
                {"event_id": event_id},
            )
