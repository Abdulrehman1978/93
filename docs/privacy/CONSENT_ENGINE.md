# Packet 06 — Consent and Lawful-Processing Engine

The engine separates three decisions:

1. a notice was presented under a specific policy version;
2. a person granted, declined, or revoked one named purpose; and
3. a server-derived `ProcessingAuthorization` permits a processing scope.

Consent is not requested for purposes whose lawful basis is voluntary specified-purpose intake, state function, or legal obligation. Optional consent is unbundled and can be declined without removing the text-only intake alternative. Emergency purposes are prohibited to anonymous sessions and require an active authenticated human supervisor; AI and system actors cannot authorize an emergency override.

## Ledger guarantees

- `ConsentEvent` is append-only and records interaction, pseudonymous subject, purpose, policy version, canonical channel, served locale, translation truth status, action ID, and predecessor.
- `GRANTED` creates an interaction-scoped authorization with authority `CONSENT`.
- `REVOKED` appends a new event and marks active consent authorizations revoked; prior events remain unchanged.
- stale policy versions, unknown purposes, invalid transitions, missing notices, and idempotency conflicts fail closed.
- case binding promotes active authorizations to case scope after subject equality is verified; it does not rewrite the original interaction ledger.

Packet 06 is DPDP-ready architecture work, not a legal certification. Operational retention, data-principal request workflows, and provider handoffs remain later packet responsibilities.
