# ADR-002: PostgreSQL Domain Schema Foundation

Status: Accepted for Packet 03 implementation, pending owner review.

## Decision

Use PostgreSQL 16.15+ as the sole canonical relational database. SQLAlchemy 2.x async with asyncpg owns runtime access; Alembic owns reproducible schema changes. Packet 03 contains 36 core tables, below the 45-table ceiling, grouped into six readable migrations.

The schema is normalized around the approved domain distinctions:

- `cases` are administrative containers, not assessments, calls, or referrals.
- `consent_events` are append-only consent choices; `processing_authorizations` are the broader lawful-authority ledger.
- transcript segments remain the source material; evidence stores pointers and provenance.
- immediate safety, SVI, and reported incident urgency are independent result tables.
- referral state, support outcomes, service freshness, service availability, service capacity, and integration status are independent.
- domain histories and audit events are separate append-oriented records.

## Modeling choices

Stable product statuses use `TEXT/VARCHAR` plus named check constraints, allowing controlled evolution without irreversible PostgreSQL ENUM types. Lawful authorities are a catalog with effective dates and source classes. JSONB is limited to variable external metadata/provenance; core domain fields are typed columns.

PII is minimized and separated: `subjects` is deliberately small, `subject_contacts` owns contact channels, and transcript/evidence/referral fields do not duplicate names, phones, addresses, identity numbers, caste, or inferred attributes. Packet 04 must add encryption/key management, RBAC, purpose-scoped authorization, and RLS as appropriate; Packet 03 does not claim those controls.

AI and domain histories are append-oriented with database update guards. Authorized retention/deletion workflows remain possible because the guards protect updates, not governed deletion actions.

Raw audio has no default database path. Packet 18 must add a separately governed storage-object relationship only if explicitly authorized. A PostgreSQL-backed `async_jobs` queue is sufficient for the lean modular monolith; Redis, Kafka, Elasticsearch, event sourcing, and a separate schema service add infrastructure and consistency cost without a Packet 03 requirement.

## Consequences

The model is explainable and queryable, but sensitive source data still requires Packet 04 controls. Cross-row lawful-basis rules and valid referral transition semantics remain domain-service responsibilities rather than a large trigger workflow engine. Migration replay and `alembic check` are required CI gates.
