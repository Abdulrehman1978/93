# SAMBAL Database Semantics Handoff
## Architectural Invariants & Domain Boundaries for Packet 03

> **Status:** AUTHORITATIVE SPECIFICATION HANDOFF (PACKET 02R → PACKET 03)  
> **Scope:** Conceptual schema invariants. **STRICTLY NO SQL OR ORM TABLES IMPLEMENTED IN PACKET 02R.**  
> **Purpose:** Prevent future engineering packets from inadvertently encoding illegal, non-minimizing, or clinically/legally unsound relational structures.

---

## 1. Core Relational Invariants

When designing PostgreSQL schemas, migrations, and ORM entities in Packet 03, the following invariants are **mandatory and non-negotiable**:

### Invariant 1: Evidence References Source Rather Than Duplicating It
- Evidence rows (`assessment_evidence`) must point to the authoritative source (`source_reference`, e.g., `transcript_id#offset_start:offset_end` or `stream_chunk_id`) rather than copying sensitive complainant text or PII into every analytical row.
- An optional `display_excerpt` is permitted only where strictly necessary for operator UI rendering, and must inherit access-control and redaction rules from the parent case.

### Invariant 2: Three Assessment Dimensions Remain Formally Independent
- The database schema must **never** coalesce, collapse, or mathematically fuse:
  1. `immediate_safety_state` (`NO_IMMEDIATE_SIGNAL`, `REVIEW_RECOMMENDED`, `ELEVATED`, `CRITICAL_REVIEW`, `INSUFFICIENT_INFORMATION`)
  2. `svi_band` (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`)
  3. `reported_urgency_level` (`ROUTINE`, `PRIORITY`, `URGENT`, `CRITICAL`)
- They must exist as separate, uncoupled attributes in the assessment entity. No database trigger or generated column may compute one from another.

### Invariant 3: Zero Additive SVI Weights in Evidence Tables
- Evidence items describe detected signals, modalities, confidence scores, and timestamps.
- The schema must **not** contain an `svi_weight`, `score_contribution`, or `numeric_delta` column. SVI computation is qualitative and multidimensional; empirical fusion models belong to Packet 11.

### Invariant 4: AI Output Is Immutable After Generation
- When an AI model emits an inference or classification, that record is **write-once / append-only**.
- It must never be mutated, updated in-place, or overwritten when a human operator reviews or overrides it.

### Invariant 5: Human Review Is Appended Non-Destructively
- Operator overrides, supervisor approvals, and human notes are stored in a dedicated `human_decisions` / `overrides` audit ledger referencing the original assessment ID.
- The record must capture:
  - `original_ai_output`
  - `human_action` (`ACCEPT`, `MODIFY`, `DISMISS`, `ESCALATE`, etc.)
  - `reason_code` and free-text justification
  - `actor_id` (authenticated operator)
  - `policy_version`
  - `timestamp`

### Invariant 6: Lawful Basis Is Distinct from Consent
- `lawful_basis` and `consent` must not be conflated into a single boolean or table.
- A `processing_authorizations` table records the legal basis (`STATE_FUNCTION_UNDER_LAW`, `LEGAL_OBLIGATION`, `MEDICAL_EMERGENCY`, `PUBLIC_ORDER_OR_DISASTER_ASSISTANCE`, `CONSENT`, `VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE`).
- A separate `consent_records` ledger tracks granular, unbundled consent choices, notice versions, and revocations for activities where consent is the legal basis.

### Invariant 7: Referral State Is Independent from Case Status
- `Referral.COMPLETED != Case.CLOSED`.
- A case is an ongoing administrative container for citizen grievance redressal, investigations, and multi-agency support.
- A referral is an operational task directed to an external service agency (e.g. DLSA, Tele-MANAS, Shelter).
- A case may have multiple concurrent referrals across different states (`REFERRED`, `CONTACTED`, `SERVICE_STARTED`, `UNABLE_TO_CONTACT`). Closing a referral does not close the case; closing a case requires an authorized officer administrative sign-off.

### Invariant 8: Service Freshness and Integration Status Are Distinct Attributes
- The service registry entity (`support_services` / `resources`) must independently store:
  - `freshness_status`: `VERIFIED_CURRENT`, `STALE`, `UNKNOWN` (records currency of directory data)
  - `integration_status`: `NOT_CONFIGURED`, `SANDBOX`, `ADAPTER_READY`, `LIVE`, `DEGRADED`, `DISABLED` (records technical software adapter readiness)
  - `availability_status` (operational hours/status)
  - `capacity_status` (available caseload slots, if reported by provider)
- Do not overload endpoint validity with integration readiness.

### Invariant 9: Support Outcome Evidence Records Provenance and Confidence
- Delivered support verification must track `outcome_evidence`:
  - `UNVERIFIED`
  - `PROVIDER_CONFIRMED`
  - `CITIZEN_CONFIRMED`
  - `DUAL_CONFIRMED` (gold standard)
  - `DOCUMENT_CONFIRMED`
  - `UNABLE_TO_VERIFY`
- `UNABLE_TO_VERIFY` must never be equated with "support failed" or "unmet need". It simply denotes that confirmation could not be obtained.

### Invariant 10: Ephemeral Audio Doctrine — Zero Default Disk Storage
- Voice data streaming chunks are processed transiently in RAM.
- No `audio_file_path` or `recording_blob` column may be mandatory or populated by default.
- If raw audio retention is authorized under explicit unbundled consent or court order (`PURP-06`), it references an encrypted object store with an explicit lifecycle tracking `deletion_state`:
  `DELETION_REQUESTED` → `PRIMARY_OBJECT_DELETED` → `RETENTION_HOLD` → `BACKUP_EXPIRY_PENDING` → `DELETION_VERIFIED`.

---

## 2. Entity Relationship Outline (Conceptual Only)

```text
 [Citizen / Case] 1 ────────── * [Case Assessments] (Immutable AI Output)
        │                               │
        │ 1                             │ 1
        │                               ▼
        │                         * [Assessment Evidence] (Minimizing Source Pointers)
        │                               │
        │                               ▼
        │                         * [Human Review Ledger] (Append-Only Overrides)
        │
        ├────────── 1 ────────── * [Processing Authorizations] (Lawful Basis)
        │                               │
        │                               ▼ 0..1
        │                         * [Consent Ledger] (Granular Opt-Ins & Revocations)
        │
        └────────── 1 ────────── * [Referrals] (Operational Service State)
                                        │
                                        ▼ 1
                                  [Service Registry] (Freshness vs Integration)
                                        │
                                        ▼ 1
                                  [Outcome Evidence] (Provenance & Dual Confirmation)
```

---

## 3. Scope Boundary Reminder for Packet 03

- Packet 03 will define Alembic migrations, PostgreSQL DDL, SQLAlchemy 2.0 async models, check constraints, foreign keys, and indexes enforcing these 10 invariants.
- No DDL or ORM code is written in Packet 02R.
