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

| Authorization is deny-by-default | `roles`, `actor_role_bindings`, and `access_elevations` have status/effective/expiry and no-self-grant checks | One PDP evaluates role, scope, assignment, purpose, and elevation before projection | Protected services must call the PDP | Packet 04 authorization matrix |
| Internal actor references are authoritative | Sensitive actor fields use nullable `actors.id`; external identities use named external-reference columns | Identity provider resolution maps issuer+subject to local actor | No token role claims are trusted | Packet 04 identity tests |
| Sensitive fields are encrypted at rest | Field envelope stores version, algorithm, key ID, nonce, ciphertext; key material is external | KeyProvider owns rotation and decryption | DTOs still minimize plaintext exposure | Packet 04 crypto/raw SQL tests |
| Citizen intake content is encrypted and append-only | `citizen_intake_entries.content` uses the existing encrypted field type; update/delete trigger blocks mutation; ordered unique submission sequence supports idempotency | Write/Silent service creates entries only inside the atomic case transaction | Authorized field scopes are required for plaintext reads | Packet 07 raw SQL, idempotency, and encryption tests |
| Citizen intake does not copy testimony into metadata | `interaction_events.event_metadata` and `audit_events.safe_metadata` contain mode/count/reference only | Intake service never writes narrative/contact values to generic JSON | Logs and external adapters receive no narrative field | Packet 07 metadata regression test |

Historical migration revisions are immutable snapshots. A static test rejects ORM/model imports and metadata-table creation from `backend/alembic/versions`; the replay gate proves `upgrade head -> downgrade base -> upgrade head -> alembic check` on PostgreSQL 16.15.

Transactional boundaries are: case + first interaction; assessment + evidence + model run; review + assessment state change; referral + first event; and consent event + authorization update. These operations belong in one application transaction when implemented.

## Packet 06 invariants

| Invariant | Database enforcement | Test/evidence |
| --- | --- | --- |
| Pre-case interaction has authoritative subject | `interactions.subject_id NOT NULL`; nullable `case_id`; RESTRICT subject FK | migration backfill and Packet 06 integration test |
| Session credential is non-reversible at rest | SHA-256 digest column, unique partial index, expiry/idle fields | token-digest test and session policy |
| Channel metadata is bounded | `validate_channel_metadata(jsonb)` check function | migration and metadata adversarial test |
| Interaction event history is append-only | update/delete trigger plus source-reference idempotency index | append-only integration test |
| Consent is interaction-scoped and idempotent | interaction/action unique partial index; append-only consent trigger | Packet 06 grant/revoke/idempotency test |
| Emergency processing needs a human | service rejects anonymous/system/AI authority; supervisor role and allowed authority required | processing authorization service |
