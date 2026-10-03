# Packet 04 Authorization Threat Model

| Threat | Control | Verification |
| --- | --- | --- |
| Horizontal case-ID substitution | Case existence, org/jurisdiction scope, assignment, generic 404/403 | Authorization integration tests |
| Vertical privilege escalation | Explicit action registry; system admin has no content permission | Role matrix tests |
| Provider referral enumeration | Exact `assigned_provider_actor_id`; provider projection | Assigned/unassigned referral tests |
| Forged or stale token | Signature, issuer, audience, time, algorithm, `kid`, JWKS refresh | OIDC adversarial tests |
| Token role injection | Roles loaded only from active database bindings | Identity contract and service tests |
| Purpose laundering | Sensitive actions require exact active processing authorization | Purpose tests |
| Elevation persistence | Mandatory expiry, scope, approval separation, status | Break-glass tests and DB checks |
| Plaintext database disclosure | AES-GCM field envelope and key-provider boundary | Raw SQL encryption test |
| Audit leakage | Safe metadata only, structured redaction, no bearer/token/narrative payload | Logging tests |
| Policy drift | Versioned permission registry, audit policy version, migration replay/drift gates | CI commands and result artifact |

Remaining deployment risks are external to this packet: IdP tenant configuration, key custody/rotation operations, database owner permissions, secret delivery, ingress CSRF enforcement, and production RLS decision implementation.
