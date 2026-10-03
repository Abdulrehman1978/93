# SIH26093 Packet 03 — PostgreSQL Domain Foundation

**Status:** PARTIAL — database implementation and gates pass; repository E2E/security verification and owner review remain pending  
**Owner Authorization:** PENDING  
**Packet:** 03  
**Date:** 2026-10-03

## Objective

Build the smallest constrained PostgreSQL foundation for SAMBAL while preserving data minimization, independent safety dimensions, provenance, lawful-basis/consent separation, independent case/referral lifecycles, and append-oriented histories.

## Delivered artifacts

- SQLAlchemy 2.x async models under `backend/app/db/models/`.
- Six readable Alembic migrations from reference catalogs through platform governance.
- PostgreSQL-only async configuration and metadata drift target.
- Deterministic `db-migrate`, `db-reset`, `db-seed`, `db-check`, `db-drift`, and `db-test` commands.
- PostgreSQL integration/privacy tests in `backend/tests/test_database_schema.py`.
- [`PII_CLASSIFICATION.md`](../data/PII_CLASSIFICATION.md), [`DATA_DICTIONARY.md`](../data/DATA_DICTIONARY.md), [`ERD.md`](../data/ERD.md), and [`SCHEMA_INVARIANTS.md`](../data/SCHEMA_INVARIANTS.md).
- [`ADR-002-DATABASE-DOMAIN-SCHEMA.md`](../architecture/ADR-002-DATABASE-DOMAIN-SCHEMA.md).

## Pre-flight corrections

- Updated the 02R result terminology to state Bharatiya Sakshya Adhiniyam, 2023 — Section 63 as the current baseline, with Indian Evidence Act, 1872 — Section 65B limited to legacy/saved proceedings where BSA Section 170 applies.
- Kept SHA-256 as an internal security policy concept, not a statutory requirement.
- Replaced absolute anonymization language with documented risk-state terminology and made clear that synthetic voice transformation is not automatically anonymization.
- Preserved the bounded research retention rule: archival remains retention and requires deletion or a formally approved versioned extension.
- Verified the processing-purpose register packet references against the authoritative progress tracker; no stale referral/Evidence Timeline or AI/Judge Lab mapping remains.

## Schema inventory

The core table count is **36** (ceiling: 45). Tables are listed in the data dictionary and grouped as:

1. Reference/governance: 5
2. Subjects/cases/interactions: 9
3. Privacy authorization: 2
4. Assessment/evidence: 7
5. Resources/referrals/follow-up: 9
6. Platform governance: 4

## Migration inventory

| Revision | Scope |
| --- | --- |
| `0001_reference_governance` | Jurisdictions, organizations, policy versions, processing purposes, authority catalog |
| `0002_casework_interactions` | Subjects, contacts, cases, status history, interactions, events, transcript segments, translations |
| `0003_privacy_authorization` | Consent event ledger and lawful processing authorizations |
| `0004_assessment_evidence` | Assessment parent, three independent result tables, model runs, evidence, reviews |
| `0005_resources_referrals` | Resources, verification history, referrals, events, outcomes, follow-up/attempt policies and history |
| `0006_platform_governance` | Async jobs, integration events, audit events, deletion requests |

## Constraints and indexes

Named checks cover UUID scope, status catalogs, confidence/quality bounds, non-negative offsets, end-before-start errors, effective date ranges, positive policy intervals, retry bounds, deletion verification completion, and required source references. Foreign keys use explicit `RESTRICT`, `CASCADE`, or `SET NULL` decisions in the model. Foundational indexes cover urgent case queues, case interaction history, assessment/evidence retrieval, pending referrals, due follow-ups, available jobs, integration idempotency, audit history, and resource lookup.

## Security and privacy truth

The schema has no raw-audio path, voiceprint, credibility score, lie score, caste-inferred field, SVI weights, generic risk score, or mandatory raw testimony copy. PostgreSQL constraints and append-only update guards are present. Packet 03 does **not** complete encryption/key management, RBAC, purpose-scoped authorization, or RLS. It supports future authorization only.

AI rows do not mean AI is operational. ASR remains baseline candidate/not live; text safety and affective AI are not started; SVI remains provisional/not implemented; government integrations remain adapter-ready/sandbox as applicable.

## Verification record

| Gate | Result |
| --- | --- |
| Fresh PostgreSQL migration | PASS — local PostgreSQL 16.15 replayed from base to head |
| Downgrade/upgrade replay | PASS — `downgrade base` then `upgrade head` |
| Alembic schema drift | PASS — `alembic check`: no new upgrade operations |
| Database integration tests | PASS — 34 passed against PostgreSQL |
| Ruff / mypy / existing pytest | PASS — format/check clean; strict mypy clean; 34 backend tests passed |
| OpenAPI | PASS — 4 paths generated |
| Frontend format/type/lint/unit/build | PASS — existing gates green; 4 frontend unit tests passed |
| Frontend Playwright E2E/a11y | UNVERIFIED — local runner hung after starting 3 tests; no pass claimed |
| Dependency/security scans | Not run locally; CI remains the authoritative gate |
| CI run IDs | None recorded yet |

## Known limitations

- Packet 04 must add encryption/key management, identity-backed actor references, RBAC/purpose scopes, and RLS where justified.
- Cross-row lawful-basis matching and referral transition semantics remain application-domain rules; no large trigger workflow engine was introduced.
- The local verification database and demo seed are synthetic/local only; no live provider, government, or AI integration is claimed.

## Packet 04 handoff

Start only after owner review. Packet 04 owns Authorization, RBAC, identity-backed actor references, field encryption/key management, retention enforcement, and privacy access controls. Do not treat this result as owner approval.

**Commit SHA:** `630af94` (amended below only if this metadata line changes)  
**Repository cleanliness:** Packet 03 changes are committed; one generated `apps/web/tsconfig.tsbuildinfo` diff from the local frontend build remains intentionally unstaged.
