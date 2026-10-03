# Packet 04 Authorization Model

Status: Implemented baseline; owner approval and deployment-specific policy review remain required.

## Decision

Every protected operation crosses one application Policy Enforcement Point (PEP) and one Policy Decision Point (PDP). The PDP is `backend/app/security/authorization.py`; FastAPI dependencies and domain services are PEPs. The default is deny. The PDP evaluates the authenticated local `Actor`, active role bindings, action, object, organization, jurisdiction ancestry, case assignment, provider assignment, processing purpose, policy version, and any short-lived elevation.

The external identity provider authenticates a subject. It does not grant application permissions. The application resolves `(issuer, subject, provider_code)` to an active local `actor_id`, then loads roles from PostgreSQL. Token role claims are ignored.

## Evaluation order

1. Reject unknown actions.
2. Require an active actor and at least one active, time-valid role binding.
3. Resolve the target object/case and return a generic not-found decision when it does not exist.
4. Match role permission and organization/jurisdiction scope. A binding to an ancestor jurisdiction may cover a descendant case; an unrelated or broader reverse scope does not.
5. Require case assignment for `HELPLINE_OPERATOR` and `CASE_OFFICER` case actions.
6. Require the exact assigned referral for service-provider roles.
7. For sensitive actions, require a purpose header/context and an active matching `processing_authorizations` row.
8. Permit an exceptional action only when the actor has `access.break_glass` and an active, scoped `access_elevations` row.
9. Append a safe allow/deny authorization audit event before returning the decision.

The public API exposes only a generic 403 or 404-style response. Internal reason codes are retained for audit and tests but are not returned as a policy oracle.

## Scope rules

Organization scope is exact. Jurisdiction scope is hierarchical upward from the resource jurisdiction. Case assignment and referral assignment are object-level constraints, not client-supplied hints. Projection services select explicit DTO fields after authorization; ORM objects are not serialized directly.

## Separation of duties

`SYSTEM_ADMIN` manages actors, roles, and resources but has no case-content permission. `AUDITOR` can inspect security/consent metadata but cannot read transcript or contact content. Provider roles have referral-safe-handoff permissions only and must be assigned to the specific referral. Role grants and elevations cannot be self-approved at the database layer.

## References

- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) — deny by default and least privilege.
- [OWASP Authorization Patterns Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Patterns_Cheat_Sheet.html) — PDP/PEP separation and resource-local enforcement.
- [OWASP API1:2023 Broken Object Level Authorization](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/).
