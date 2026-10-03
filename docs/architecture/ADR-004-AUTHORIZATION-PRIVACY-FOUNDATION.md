# ADR-004: Authorization and Privacy Foundation

Status: Implemented in Packet 04; owner review pending.

## Decision

Use a provider-neutral OIDC/OAuth authentication boundary mapped to local actors, a code-versioned hybrid RBAC/ABAC policy registry, and one application PDP/PEP path for protected operations. Enforce object-level organization, jurisdiction, case-assignment, provider-referral, purpose, and lawful-processing scopes before explicit DTO projection. Use AES-256-GCM envelopes for highly sensitive fields with keys outside PostgreSQL/source. Record safe authorization decisions in append-only audit events.

The five-table security foundation is `actors`, `actor_identities`, `roles`, `actor_role_bindings`, and `access_elevations`. Internal actor references use foreign keys; external identity references remain explicitly named.

## Rejected or deferred choices

- Provider SDKs and token role claims are rejected at the domain boundary.
- Production local-password fallback is rejected.
- Generic administrator access to case content is rejected.
- PostgreSQL RLS is deferred because the current policy combines role, assignment, purpose, hierarchy, and break-glass state; the formal gate is in `docs/security/RLS_DECISION.md`.
- UI redesign and Packet 05 work are out of scope.

## Consequences

The application must pass a principal and authorization context to protected services, and every new action requires registry, projection, audit, and adversarial-test review. Deployment owners must configure the concrete IdP, secret provider, CSRF/token delivery, database privileges, and break-glass operations.
