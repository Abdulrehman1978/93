# Packet 03 PII Classification

Status: Packet 04 baseline implemented; deployment-specific key custody, IdP configuration, and RLS remain external/review controls.

| Classification | Packet 03 examples | Required future controls |
| --- | --- | --- |
| `PUBLIC` | Reference codes, service types, policy version identifiers, non-sensitive status catalogs | Ordinary application authorization and integrity checks |
| `INTERNAL` | Case status, queue priority, operational timestamps, provider integration state, job state | Packet 04 organization/jurisdiction scope and operator authorization |
| `CONFIDENTIAL` | Public tracking ID, case/referral identifiers, audit entity references, service contact endpoints | Scoped access, redaction, retention enforcement, secure logging |
| `HIGHLY_SENSITIVE` | Subject contacts, transcript content, assessment evidence source pointers, consent history, referral authorization links, support outcome provenance | Packet 04 field encryption/key management, purpose-scoped authorization, access logging, retention/deletion workflows |
| `SECURITY_METADATA` | Model/provider provenance, idempotency keys, correlation IDs, audit safe metadata, deletion state | Tamper-evident handling, restricted access, retention schedule, no testimony or credential payloads |

## Column-level decisions

| Table / columns | Classification | Notes and future owner |
| --- | --- | --- |
| `subjects.subject_reference`, `subjects.classification` | `CONFIDENTIAL` | Minimal operational identity state; no name, phone, address, identity number, caste, religion, age, gender, or voice-derived attribute. Packet 04 owns subject identifier protection. |
| `subject_contacts.contact_value`, `safe_to_use` | `HIGHLY_SENSITIVE` | Only necessary contact channels; `contact_value` is stored as an AES-256-GCM envelope through the field-encryption boundary. |
| `cases.public_tracking_id` | `CONFIDENTIAL` | Safe random/non-semantic public identifier; never derived from phone, district, caste, or date. |
| `transcript_segments.content` | `HIGHLY_SENSITIVE` | Authoritative narrative source. Packet 04 owns encryption and purpose-scoped access. No assessment copy is stored. |
| `translations.translated_content` | `HIGHLY_SENSITIVE` | Derived representation; original transcript remains authoritative. |
| `assessment_evidence.source_reference`, offsets, provenance | `HIGHLY_SENSITIVE` / `SECURITY_METADATA` | Pointer and provenance only; no mandatory raw snippet or narrative copy. |
| `consent_events.*` | `HIGHLY_SENSITIVE` | Append-only purpose-specific consent ledger; no IP/device metadata by default. |
| `processing_authorizations.*` | `CONFIDENTIAL` / `SECURITY_METADATA` | Legal authority and scope, separate from consent. Packet 04 owns actor identity and authorization enforcement. |
| `service_resources.contact_endpoint` | `CONFIDENTIAL` | Directory contact information; keep separate from freshness, availability, capacity, and integration status. |
| `referrals.*`, `support_outcomes.*`, `follow_ups.*`, `contact_attempts.*` | `HIGHLY_SENSITIVE` | Operational support history and safe-contact decisions. Packet 04 owns purpose-scoped access and redaction. |
| `model_runs.*`, `integration_events.*`, `async_jobs.*` | `SECURITY_METADATA` | References and metadata only; no raw prompts, victim testimony, credentials, or tokens. |
| `audit_events.safe_metadata` | `SECURITY_METADATA` | Safe metadata only. Never store transcript, narrative, raw audio, credentials, or authorization tokens. |
| `deletion_requests.*` | `SECURITY_METADATA` | Governed deletion/retention state; `DELETION_VERIFIED` is not valid until controlled systems complete deletion. |

## Explicitly absent in Packet 03

The schema intentionally has no raw audio path, voiceprint, credibility score, lie score, inferred caste field, research corpus, vector embedding, facial analysis, or generic narrative JSON field. Packet 04 implements the application authorization and encryption baseline; RLS is explicitly deferred under `docs/security/RLS_DECISION.md`.
## Packet 07 additions

| Data element | Classification | Storage rule | Access / retention boundary |
| --- | --- | --- | --- |
| `citizen_intake_entries.content` | Highly sensitive citizen-provided narrative or answer | AES-256-GCM envelope through existing `EncryptedText`; no generic JSON or log copy | Interaction/case retention; authorized field-decryption scope only |
| `citizen_intake_entries.client_submission_id` | Security metadata / opaque client retry key | Stored as a bounded opaque value; never a content or identity field | Used only for same-session idempotency |
| `subject_contacts.contact_value` from citizen intake | Highly sensitive contact detail | Existing encrypted `subject_contacts.contact_value`; `safe_to_use = false` on intake | No contact delivery or dispatch in Packet 07 |
