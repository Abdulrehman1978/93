# Packet 04 Identity Provider Contract

## Boundary

`backend/app/security/identity.py` defines a provider-neutral `IdentityProvider` protocol. The shipped implementation is a small OIDC/OAuth-compatible JWT verifier using PyJWT, cryptography, and HTTP JWKS retrieval. No provider SDK or vendor-specific import is permitted in the domain layer.

## Required token checks

Validation fails closed unless all of the following hold: signature verifies against a JWKS key identified by `kid`; `alg` is in the approved configuration; `iss`, `aud`, `sub`, `exp`, and `nbf` are valid within bounded clock skew; the token is structurally valid; and the key is available. Unknown `kid` causes a refresh, then denial if still unavailable. JWKS is cached with a bounded lifetime and refreshed on rotation/miss.

The service maps `(issuer, subject, provider_code)` to one active `actor_id` through `actor_identities`. Revoked identities, inactive actors, malformed tokens, wrong issuer/audience, expired tokens, unsupported algorithms, and unknown keys all return the same safe authentication failure class. No local production password fallback exists.

## Deployment contract

Production must provide issuer, audience, JWKS URI, approved algorithms, clock skew, and cache settings. Production field-encryption keys must come from an external secret boundary. Token storage is not specified as browser local storage; deployments must use an HttpOnly/Secure/SameSite cookie or an equivalent controlled bearer-token channel with CSRF protection where cookies are used. CORS origins are explicit; wildcard production origins are rejected.

## Standards references

- [NIST SP 800-63-4](https://pages.nist.gov/800-63-4/) — current digital identity, authentication, and federation guidance (published 2025).
- [OWASP API Security Top 10, API2:2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/) — broken authentication risk.
