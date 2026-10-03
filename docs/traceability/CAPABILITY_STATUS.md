# Capability Truth State Register

> **Document ID:** CAPABILITY-STATUS-REGISTER-V2  
> **Standard:** Absolute transparency on runtime status. Zero fabricated integrations, zero fake "live" badges.  
> **Allowed States:** `FOUNDATION_READY` | `BASELINE_CANDIDATE` | `SPECIFIED` | `PROVISIONAL_TRIAGE_POLICY` | `ADAPTER_READY` | `SANDBOX` | `RESEARCH_ONLY` | `NOT_STARTED`  

---

## 1. Capability Status Matrix (Post-Packet 04 Review)

| Capability / Module | Runtime Truth State | Operational Description & Execution Boundary | Evidence Artifact / Provider |
| :--- | :--- | :--- | :--- |
| **Monorepo Foundation & Quality Gates** | `FOUNDATION_READY` | Node 24, Next.js 16 Active-LTS, Python 3.12, uv 0.12.17, Ruff, Mypy, Vitest, Playwright, Axe, Gitleaks, pip-audit, npm audit. | Verified on GitHub Actions Runs `37096095377` and `37096375263`. |
| **Local Indic ASR (Speech-to-Text)** | `BASELINE_CANDIDATE` | Initial local implementation candidate using CTranslate2 INT8 `faster-whisper-turbo`. Final selection subject to Packet 08 benchmarking against Indic-focused/government alternatives. | `backend/app/intelligence/contracts.py` (ASRProvider); benchmark suite in Packet 08. |
| **Three-Dimensional Assessment Model** | `SPECIFIED` | Formal separation of Immediate Safety, SVI, and Reported Incident Urgency with qualitative evidence precedence rules. | `docs/product/ASSESSMENT_MODEL.md`; `packages/contracts/src/index.ts`. |
| **Immediate Safety State Machine** | `SPECIFIED` | 5 authoritative states (`NO_IMMEDIATE_SIGNAL`, `REVIEW_RECOMMENDED`, `ELEVATED`, `CRITICAL_REVIEW`, `INSUFFICIENT_INFORMATION`). | `docs/product/IMMEDIATE_SAFETY_POLICY.md`; `packages/contracts/src/index.ts`. |
| **Self-Harm & Suicide Safety Protocol** | `SPECIFIED` | Non-diagnostic principle, 7-part context semantics taxonomy, and mandatory human crisis de-escalation workflow. | `docs/product/SELF_HARM_SAFETY_POLICY.md`; `docs/ai/GOLDEN_SAFETY_CORPUS.md`. |
| **Reported Incident Urgency Model** | `SPECIFIED` | 4 objective urgency levels (`ROUTINE`, `PRIORITY`, `URGENT`, `CRITICAL`), completely decoupled from emotional presentation. | `docs/product/REPORTED_INCIDENT_URGENCY.md`. |
| **Stress Vulnerability Index (SVI)** | `PROVISIONAL_TRIAGE_POLICY` | Conceptual triage bands (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`). Mathematical fusion formula is explicitly unencoded in Packet 02 and deferred to Packet 11. | `docs/ai/SVI_POLICY.md`; `packages/contracts/src/index.ts`. |
| **Affective Distress / Acoustic Signals** | `RESEARCH_ONLY` | Designated strictly as `SUPPORTING_SIGNAL_ONLY`. Legally forbidden from determining urgency or causing emergency dispatch. | `docs/ai/AFFECTIVE_SIGNAL_POLICY.md`. |
| **Consequential Action & Override Model** | `SPECIFIED` | Authority matrix (Suggest vs Prepare vs Approve vs Forbidden) and 8 non-destructive operator override actions. | `docs/product/HUMAN_OVERSIGHT.md`. |
| **Support Service Taxonomy (12 Pathways)**| `SPECIFIED` | Covers all SIH26093 expected recommendation pathways and official statutory relief mechanisms under PoA Act. | `docs/product/SERVICE_TAXONOMY.md`; `packages/contracts/src/index.ts`. |
| **Closed-Loop Referral State Machine** | `SPECIFIED` | 15-state lifecycle and 7-tier Verified Support Hierarchy answering "Did support actually arrive?". | `docs/product/REFERRAL_STATE_MACHINE.md`. |
| **Safe Handoff & Never-Repeat-My-Story**| `SPECIFIED` | Role-based data minimization per agency (Counsellor, Legal, Medical, ERSS) and multi-layer memory architecture. | `docs/product/SAFE_HANDOFF.md`. |
| **DPDP Granular Consent Model** | `SPECIFIED` | 7 unbundled purpose-specific consent dimensions; research and raw audio retention strictly optional. | `docs/privacy/CONSENT_MODEL.md`. |
| **Raw Audio Ephemeral Streaming Policy** | `SPECIFIED` | In-memory ephemeral processing; zero default disk persistence; AES-256-GCM encryption if consented. | `docs/privacy/DATA_MINIMIZATION.md`. |
| **Trauma-Informed UX & Civic Calm** | `SPECIFIED` | 5 trauma-informed pillars, calming visual tokens, persistent Quick Exit, and discreet Silent Distress mode. | `docs/product/TRAUMA_INFORMED_UX.md`; `docs/product/CONTENT_GUIDE.md`. |
| **Tele-MANAS Handoff Adapter (14416)** | `ADAPTER_READY` | National mental health baseline verified (20 languages, 53 cells); adapter contract established for Packet 19. | `docs/SOURCE_REGISTRY.md`; `docs/product/SERVICE_TAXONOMY.md`. |
| **NALSA / DLSA Legal Aid Adapter (15100)**| `ADAPTER_READY` | Statutory baseline verified under LSA Act Sec 12(b); adapter contract established for Packet 19. | `docs/SOURCE_REGISTRY.md`; `docs/product/SERVICE_TAXONOMY.md`. |
| **ERSS 112 Emergency Handoff Adapter** | `ADAPTER_READY` | Human-authorized emergency dispatch protocol established; adapter contract established for Packet 19. | `docs/SOURCE_REGISTRY.md`; `docs/product/SERVICE_TAXONOMY.md`. |
| **SAMBAL / NHAA Canonical Adapter** | `ADAPTER_READY` | Baseline verified against MoSJE NHAA (14566) specifications; adapter contract established for Packet 19. | `docs/SOURCE_REGISTRY.md`; `docs/research/SAMBAL_NHAA_CURRENT_STATE.md`. |
| **Bhashini MeitY Cloud ASR** | `ADAPTER_READY` | Cloud ASR fallback candidate for Packet 08 benchmarking. | `backend/app/intelligence/contracts.py`. |
| **Canonical PostgreSQL Container** | `FOUNDATION_CONTAINER_READY` | Pinned `postgres:16.15-alpine` running on port 5493. Domain tables and Alembic migrations scheduled for Packet 03. | `docker-compose.yml`; verified healthy in clean CI. |
| **MinIO Object Storage Container** | `FOUNDATION_CONTAINER_READY` | Pinned release tag `quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z` on port 9093 with non-blocking readiness. | `docker-compose.yml`; verified healthy in clean CI. |
| **Identity, Authorization & Privacy Foundation** | `FOUNDATION_READY` | Provider-neutral OIDC boundary, deny-by-default RBAC/ABAC PDP/PEP, object-level scope, purpose gates, field encryption, audit decisions, and minimum-field projections. Concrete IdP/key custody and RLS remain deployment/Packet 27 gates. | `docs/security/`; `backend/app/security/`; `docs/results/04-result.md`. |

---

## 2. Transition Gate Requirements
- **To move from `SPECIFIED` to `LIVE` / `IMPLEMENTED`:** Requires completion of the corresponding downstream packet (Packet 03 for DB, Packet 04 for Auth, Packet 05/07 for Citizen UI, Packet 08 for Speech, Packet 09 for NLP, Packet 10 for Audio ML, Packet 11 for SVI Fusion, Packet 13 for Operator Copilot, Packet 15 for Referrals), with 100% passing automated unit, integration, and E2E tests.
- **To move from `ADAPTER_READY` to `LIVE`:** Requires formal ministerial peering, production credentials, and signed data-sharing agreements.
