# Packet 04R Result — Authorization Trust-Boundary, Encryption Enforcement & Break-Glass Remediation

Status: OWNER APPROVED — PASS.

Owner Review: APPROVED

Final commit: `eb772e7615203cb94778e9675e487b9a8fb65b73`
GitHub Actions: `37117506534` — SUCCESS

## Objective

Close the Packet 04 security gaps without changing the architecture: derive persistent authorization scope from PostgreSQL, enforce encryption through normal ORM writes and authorized reads, require independent human break-glass approval, and align OIDC configuration with the implemented RSA verifier.

## Delivered

- Split caller request facts, opaque resource references, intended creation scope, and trusted resolved resource scope.
- Added one database-backed `ResourceScopeResolver` for cases, referrals, assessments, transcripts, translations, contacts, consents, processing authorizations, and support outcomes. Provider and case assignment checks use only resolved data.
- Added an explicit action/resource registry, global-action semantics, creation-scope rules, and context-spoofing denial.
- Added ORM `EncryptedText` enforcement for contact values, transcript content, and translated content. Decryption is fail-closed outside an authorized sensitive-field service, uses field-bound AAD, and supports old-key reads during rotation.
- Added distinct authorization-decision and completed-resource-read audit events. Audit records remain append-only protected by PostgreSQL update/delete guards; no cryptographic tamper-evidence claim is made.
- Added database and service enforcement that active break-glass elevations have a non-null, independent, active human approver. Self-approval and `SYSTEM` approval are rejected.
- Restricted OIDC to the implemented RSA family (`RS256`, `RS384`, `RS512`). Mandatory claims are `iss`, `aud`, `sub`, and `exp`; `nbf` is optional and validated when present.
- Preserved `SYSTEM_ADMIN` content denial and `AUDITOR` audit access while denying auditor contact/transcript content.

## Database and API changes

- Added immutable migration `0008_auth_trust_boundary` with the active-approval constraint and human-approver trigger.
- Kept the existing 41-table schema and all Packet 03/03R/04 migrations unchanged.
- Protected API routes now pass opaque resource references; they do not pre-resolve or accept authoritative case scope.

## Verification

- `pytest -q --cov=app` — 50/50 backend tests passed; 85% statement coverage.
- `alembic downgrade base`, `alembic upgrade head`, and `alembic check` — passed; full migration replay and zero schema drift.
- `ruff format --check .`, `ruff check .`, and strict `mypy app` — passed.
- OpenAPI generation — passed with seven paths.
- Frontend Prettier, TypeScript, ESLint, Vitest (4/4), and production build — passed. The three unchanged Playwright tests each reached execution locally; the Windows runner did not terminate its web-server teardown, so the remote Linux CI result remains the authoritative E2E gate.
- Security tests cover database-authoritative scope, scope spoofing, omitted caller case IDs, provider assignment, role boundaries, purpose matching, human break-glass approval, RSA algorithm rejection, optional future `nbf` rejection, field-bound AAD, key rotation, unauthorized decryption, raw ciphertext for all three protected ORM fields, and distinct actual-read audits.

## External dependencies and limitations

Production IdP tenant configuration, external KMS/HSM/Vault custody, operational key rotation, database-owner hardening, and break-glass review procedures remain deployment responsibilities. Processing-authority effective/status evaluation is intentionally deferred to Packet 06, where the consent and authority lifecycle is implemented. PostgreSQL RLS remains an explicit Packet 27 hardening decision; the application PDP is authoritative today.

## Transition gate

Packet 04R was explicitly owner-approved in the Packet 05 authorization. Packet 05 may proceed; Packet 06 remains blocked.
