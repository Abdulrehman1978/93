# SIH26093 Packet 03R — Migration Immutability, Referral Semantics & Database Verification

**Status:** PASS — implementation and local replay gates pass; final remote CI verification recorded below
**Owner Review:** OWNER APPROVED
**Packet:** 03R (remediation of Packet 03)  
**Date:** 2026-10-03

## Scope and blocker resolved

Packet 03R remediates the Packet 03 migration-history defect: all six historical revisions previously imported current SQLAlchemy models and created tables through `Base.metadata`. Historical revisions are now immutable, self-contained Alembic snapshots using explicit `op.create_table`, index, constraint, trigger, and drop operations. No revision imports `app.db`, `app.db.models`, `Base.metadata`, or `metadata.tables[...]`.

The six logical revisions remain unchanged:

1. `0001_reference_governance`
2. `0002_casework_interactions`
3. `0003_privacy_authorization`
4. `0004_assessment_evidence`
5. `0005_resources_referrals`
6. `0006_platform_governance`

A static integration gate rejects ORM/model imports and metadata-table creation in `backend/alembic/versions`. Append-only trigger lifecycle remains explicit: the function is created in revision 0002, triggers are created by the owning revisions, and downgrades remove triggers before the function.

## Domain corrections

- `referrals.status`, `referral_events.previous_status`, and `referral_events.new_status` now accept exactly: `RECOMMENDED`, `REVIEW_REQUIRED`, `APPROVED`, `DECLINED`, `REFERRED`, `ACKNOWLEDGED`, `CONTACT_PENDING`, `CONTACTED`, `APPOINTMENT_SCHEDULED`, `SERVICE_STARTED`, `FOLLOW_UP_DUE`, `COMPLETED`, `UNABLE_TO_CONTACT`, `ESCALATED`, `CANCELLED`. The default is `RECOMMENDED`; `DRAFT` is removed.
- `support_outcomes.outcome_stage` now has its own seven-state check: `RECOMMENDED`, `REFERRED`, `ACKNOWLEDGED`, `CONTACTED`, `SERVICE_STARTED`, `FOLLOW_UP_CONFIRMED`, `COMPLETED`. Evidence state remains a separate six-state dimension.
- `cases.status`, referral state, outcome stage, and outcome evidence remain independent; referral completion does not close a case.
- `processing_authority_types.source_class` is explicitly renamed to `authority_source_class`, with the independent authority catalog values `STATUTORY`, `REGULATORY`, `CONSTITUTIONAL`, `EXECUTIVE_POLICY`, `PRODUCT_POLICY`. This is documented as distinct from the Packet 02R policy/configuration source taxonomy.
- `contact_attempt_policies.safe_callback_start` and `safe_callback_end` now use PostgreSQL `TIME` for local wall-clock callback windows.
- `*.tsbuildinfo` is ignored and the tracked generated `apps/web/tsconfig.tsbuildinfo` artifact is removed from version control.

## Verification matrix

| Gate | Result |
| --- | --- |
| PostgreSQL version | PASS — local PostgreSQL 16.15 |
| Fresh migration | PASS — `alembic upgrade head` from base |
| Replay migration | PASS — `upgrade head -> downgrade base -> upgrade head` |
| Schema drift | PASS — `alembic check` reports no new upgrade operations |
| Schema budget | PASS — 36 public tables excluding `alembic_version`; ceiling 45 |
| Backend tests | PASS — 37 tests passed, including full referral vocabulary, unknown-value rejection, outcome stage/evidence separation, TIME columns, and migration static gate |
| Ruff / mypy | PASS — format check, lint, and strict mypy |
| Frontend | PASS — Prettier, contracts build, typecheck, ESLint, 4 Vitest tests, and Next production build |
| Playwright/Axe | UNVERIFIED locally — the 3-test Playwright runner hung after startup and was stopped; no local pass is claimed |
| Gitleaks | UNVERIFIED locally — executable unavailable; CI remains authoritative |
| npm audit | UNVERIFIED locally — registry audit endpoint was unavailable |
| pip-audit | UNVERIFIED locally — package is not installed in the local environment |

## Baseline and repository evidence

- Original Packet 03 implementation commit: `630af94`.
- Original Packet 03 verification commit: `de945ac`.
- Original recorded green CI run: [GitHub Actions run 37109287211](https://github.com/Abdulrehman1978/93/actions/runs/37109287211).
- The original Packet 03 partial result remains preserved in [`03-result.md`](./03-result.md); this report records the remediation and closure evidence.
- Final CI run: [GitHub Actions run 37111604427](https://github.com/Abdulrehman1978/93/actions/runs/37111604427) — **success**, head SHA `9a53c79dba39a1de945ebd610593cb6710b5779f`.
- Verified implementation commit SHA: `9a53c79`.
- Working tree: clean after the documentation-only result closure commit.

## Known limitations and stop boundary

Packet 03R does not add authentication, RBAC, RLS, field encryption, key management, retention workers, or live provider integrations. Those remain Packet 04 scope. Cross-row lawful-basis matching and legal referral transition semantics remain application-domain rules, not database triggers.

Packet 03R owner review is approved under the supplied Packet 04 authorization. Packet 04 is now the active packet; no Packet 05 work is included.
