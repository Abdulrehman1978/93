# Packet 04 RLS Decision

Decision: defer PostgreSQL Row-Level Security for this packet and require the application PDP/PEP as the authoritative enforcement layer for the current modular monolith.

Reasoning:

- The policy is not a single tenant predicate: it combines actor role, effective time, organization, jurisdiction ancestry, case assignment, provider referral assignment, purpose, lawful processing authorization, and break-glass.
- Connection pooling and asynchronous request scope make an incomplete session-variable design a high-risk false assurance.
- The code has one explicit authorization service and protected projection routes, with adversarial integration coverage and generic nondisclosure behavior.

This is not permission to bypass the PDP. Every sensitive repository/service method must accept an authenticated principal and policy context. A future RLS adoption must be additive and tested in a database role that cannot disable policy, with `SET LOCAL` transaction hygiene, pool-leakage tests, migration replay, and a fail-closed comparison against the PDP. Packet 27 is the review gate for that work.
