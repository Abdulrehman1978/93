"""Print representative Packet 03 query plans against the canonical PostgreSQL database."""

from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.database import engine

QUERIES = {
    "urgent_case_queue": """
        SELECT id, public_tracking_id FROM cases
        WHERE status IN ('OPEN', 'UNDER_REVIEW') AND priority IN ('URGENT', 'CRITICAL')
        ORDER BY priority DESC, created_at
        LIMIT 50
    """,
    "case_interaction_history": """
        SELECT i.id, i.channel, i.started_at FROM interactions i
        WHERE i.case_id = '00000000-0000-0000-0000-000000000001'
        ORDER BY i.started_at
    """,
    "assessment_evidence_retrieval": """
        SELECT a.id, e.source_reference, e.source_start, e.source_end
        FROM assessments a JOIN assessment_evidence e ON e.assessment_id = a.id
        WHERE a.case_id = '00000000-0000-0000-0000-000000000001'
        ORDER BY e.created_at
    """,
    "pending_referral_queue": """
        SELECT id, case_id, next_action_at FROM referrals
        WHERE status IN ('REFERRED', 'CONTACTED')
        ORDER BY next_action_at NULLS LAST, priority DESC
        LIMIT 50
    """,
    "follow_ups_due": """
        SELECT id, referral_id, due_at FROM follow_ups
        WHERE status = 'DUE' AND due_at <= now()
        ORDER BY due_at LIMIT 50
    """,
    "resource_lookup": """
        SELECT id, provider_name, service_type FROM service_resources
        WHERE jurisdiction_id = '00000000-0000-0000-0000-000000000001'
          AND service_type = 'LEGAL_AID' AND freshness_status = 'VERIFIED_CURRENT'
    """,
    "available_jobs": """
        SELECT id, job_type FROM async_jobs
        WHERE status = 'QUEUED' AND available_at <= now()
        ORDER BY priority, available_at LIMIT 100
    """,
    "entity_audit_history": """
        SELECT id, action, occurred_at FROM audit_events
        WHERE entity_type = 'CASE' AND entity_id = '00000000-0000-0000-0000-000000000001'
        ORDER BY occurred_at
    """,
}


async def main() -> None:
    async with engine.connect() as connection:
        for name, query in QUERIES.items():
            rows = await connection.scalars(text(f"EXPLAIN (COSTS OFF) {query}"))
            print(f"[{name}]")
            print("\n".join(rows))
            print()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
