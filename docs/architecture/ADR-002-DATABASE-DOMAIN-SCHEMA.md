# ADR-002: PostgreSQL Domain Schema Foundation

Status: Accepted for Packet 03 implementation and closed by Packet 03R owner approval; Packet 04 authorization/privacy additions are in docs/security/ and migration 0007.

## Decision

Use PostgreSQL 16.15+ as the sole canonical relational database. SQLAlchemy 2.x async with asyncpg owns runtime access; Alembic owns reproducible schema changes. Packet 03 contains 36 core tables and Packet 04 adds five security tables for 41 total, below the 45-table ceiling. Each revision is an immutable, self-contained snapshot expressed with explicit Alembic operations; revisions never import current ORM models or `Base.metadata`.

The schema is normalized around the approved domain distinctions:

- `cases` are administrative containers, not assessments, calls, or referrals.
- `consent_events` are append-only consent choices; `processing_authorizations` are the broader lawful-authority ledger.
- transcript segments remain the source material; evidence stores pointers and provenance.
- immediate safety, SVI, and reported incident urgency are independent result tables.
- referral state (15 controlled states), support outcome stage/evidence, service freshness, service availability, service capacity, and integration status are independent.
- domain histories and audit events are separate append-oriented records.

## Modeling choices

Stable product statuses use `TEXT/VARCHAR` plus named check constraints, allowing controlled evolution without irreversible PostgreSQL ENUM types. Lawful authorities are a catalog with effective dates and the independent `authority_source_class` vocabulary `STATUTORY`, `REGULATORY`, `CONSTITUTIONAL`, `EXECUTIVE_POLICY`, and `PRODUCT_POLICY`. Safe callback windows use PostgreSQL `TIME` local wall-clock values. JSONB is limited to variable external metadata/provenance; core domain fields are typed columns.

PII is minimized and separated: `subjects` is deliberately small, `subject_contacts` owns contact channels, and transcript/evidence/referral fields do not duplicate names, phones, addresses, identity numbers, caste, or inferred attributes. Packet 04 adds application encryption/key management, RBAC, purpose-scoped authorization, actor identity, and explicit projections. RLS is not claimed; the decision and future adoption gate are recorded in `docs/security/RLS_DECISION.md`.

AI and domain histories are append-oriented with database update guards. Authorized retention/deletion workflows remain possible because the guards protect updates, not governed deletion actions.

Raw audio has no default database path. Packet 18 must add a separately governed storage-object relationship only if explicitly authorized. A PostgreSQL-backed `async_jobs` queue is sufficient for the lean modular monolith; Redis, Kafka, Elasticsearch, event sourcing, and a separate schema service add infrastructure and consistency cost without a Packet 03 requirement.

## Consequences

The model is explainable and queryable, but sensitive source data still requires Packet 04 controls. Cross-row lawful-basis rules and valid referral transition semantics remain domain-service responsibilities rather than a large trigger workflow engine. Migration replay and `alembic check` are required CI gates.
