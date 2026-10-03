# Packet 04 Break-Glass Policy

Break-glass is exceptional access, not a role shortcut. An elevation must identify the actor, resource type, resource/case scope, requested permission, human reason, policy source, approver, effective interval, expiry, status, and correlation ID.

Rules:

- Only a role explicitly containing `access.break_glass` can use an elevation.
- The elevation must be active, effective now, unexpired, and scoped to the requested object/case.
- Expiry is mandatory and must be after effective start; database checks reject invalid intervals.
- Every active elevation requires a non-null, active human approver whose actor type is `STAFF` or `AUDITOR`; `SYSTEM` actors cannot approve.
- The approver cannot be the requesting actor. PostgreSQL checks and a trigger enforce these rules, and the authorization service revalidates them at use time.
- The reason is operationally meaningful but never copied into sensitive content or logs.
- Every request and use is an audit event; denial and expiry are also auditable.
- Elevation does not bypass purpose authorization, object existence checks, or safe projections.
- The service returns the same generic denial surface for an absent, expired, revoked, or mismatched elevation.

Emergency access review, revocation, and retention are operational controls for the deployment owner; the schema preserves the evidence needed for that review.
