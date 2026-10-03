# Packet 04 Authorization Threat Model

| Threat | Control | Verification |
| --- | --- | --- |
| Horizontal case-ID or scope substitution | Central database-backed scope resolver; caller context cannot redefine case/org/jurisdiction/provider; generic 404/403 | Context-spoofing authorization tests |
| Vertical privilege escalation | Explicit action registry; system admin has no content permission | Role matrix tests |
| Provider referral enumeration | Exact `assigned_provider_actor_id`; provider projection | Assigned/unassigned referral tests |
| Forged or stale token | Signature, issuer, audience, time, algorithm, `kid`, JWKS refresh | OIDC adversarial tests |
| Token role injection | Roles loaded only from active database bindings | Identity contract and service tests |
| Purpose laundering | Sensitive actions require exact active processing authorization | Purpose tests |
| Elevation persistence or machine approval | Mandatory expiry, scope, independent active human approval, status | Break-glass service tests, check constraints, and trigger tests |
| Plaintext database disclosure | ORM-enforced AES-GCM fields, authorized decryption boundary, external key provider | Normal ORM writes plus raw SQL inspection for all protected fields |
| Audit leakage | Safe metadata only, structured redaction, no bearer/token/narrative payload | Logging tests |
| Policy drift | Explicit action/resource registry, versioned permissions, audit policy version, migration replay/drift gates | CI commands and result artifact |

Remaining deployment risks are external to this packet: IdP tenant configuration, key custody/rotation operations, database owner permissions, secret delivery, ingress CSRF enforcement, and production RLS decision implementation.
