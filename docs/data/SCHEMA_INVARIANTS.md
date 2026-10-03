# Packet 03 Schema Invariants

| Invariant | Database constraint or structure | Application-domain enforcement | Future authorization enforcement | Test |
| --- | --- | --- | --- | --- |
| PostgreSQL is canonical | UUID, JSONB/ARRAY, TIMESTAMPTZ, pgcrypto, and Alembic migrations; no SQLite URL accepted | Async SQLAlchemy/asyncpg only | Packet 04 scope controls run on PostgreSQL | Fresh upgrade and configuration validator |
| Evidence references source | `assessment_evidence.source_reference NOT NULL`; offsets/checks; no testimony-copy columns | Resolve excerpts at read time from an authorized source | Purpose-scoped source access and redaction | Privacy schema test |
| Three assessment dimensions stay independent | Three child tables with separate state/band/level columns; no generated columns or fusion trigger | Assessment service writes each result independently | Human review required before consequential action | Assessment dimension test |
| SVI is not prematurely scored | `svi_results.numeric_score` nullable; no weight/delta columns | Packet 11 owns evaluated scoring policy | Packet 04 restricts access to provisional outputs | No-weight and nullable-score test |
| AI outputs are append-oriented | Update triggers on model runs, results, evidence, reviews, and domain histories | Recalculation creates a new assessment/version | Authorized retention deletion remains separately governed | Append-only trigger test |
| Consent differs from lawful authority | Separate `consent_events` and `processing_authorizations`; authorization has authority catalog FK | Domain service requires the correct basis for the purpose | Packet 04 identity, role, organization, and purpose scope | Table separation and FK tests |
| Case and referral lifecycles are independent | Separate `cases.status`, 15-state `referrals.status`, `referral_events.previous_status/new_status`, and history tables | Referral transitions do not close cases; valid transitions remain domain logic | Packet 04 restricts transition actors | Full referral vocabulary integration test |
| Service dimensions are independent | Separate freshness, availability, capacity, integration columns; verification history | Directory and adapter services update each dimension separately | Packet 04 limits provider/operator edits | Resource column test |
| Support outcome is not referral state | Separate 7-stage `support_outcomes.outcome_stage` and evidence state with `UNABLE_TO_VERIFY` | Outcome collection never infers service delivery from referral existence | Packet 04 limits outcome confirmation actors | Outcome stage/evidence integration test |
| Raw audio is absent by default | No audio object/path/blob column in cases, interactions, assessments, evidence | Packet 18 must introduce an explicitly governed object relationship | Packet 04 will gate any future retained object | Forbidden-column test |
| Deletion verification is truthful | `DELETION_VERIFIED` requires `completed_at`; state is tracked separately from object data | Worker records every controlled-system completion | Packet 04 owns retention holds and approvals | Deletion-state constraint test |
| Job claims are concurrency-safe | Queue index on `(status, available_at, priority)` and reference-only payload | Future worker uses `FOR UPDATE SKIP LOCKED` | Packet 04 limits job payload access | Queue structure test |
| Audit is not domain history | `audit_events` is separate from status/event ledgers and has safe metadata only | Every consequential operation writes both where required | Packet 04 identifies actor and scope | Audit append test |

Historical migration revisions are immutable snapshots. A static test rejects ORM/model imports and metadata-table creation from `backend/alembic/versions`; the replay gate proves `upgrade head -> downgrade base -> upgrade head -> alembic check` on PostgreSQL 16.15.

Transactional boundaries are: case + first interaction; assessment + evidence + model run; review + assessment state change; referral + first event; and consent event + authorization update. These operations belong in one application transaction when implemented.
