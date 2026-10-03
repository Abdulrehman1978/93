# Packet 04 Role and Permission Matrix

The executable registry is `backend/app/security/permissions.py`, version `packet04-v1`. Database role rows are seeded by immutable migration `0007_authorization_privacy`; permission membership remains code-reviewed and versioned.

| Role | Permitted surface | Explicit boundary |
| --- | --- | --- |
| HELPLINE_OPERATOR | Assigned-case summary/sensitive read, update, contact/transcript/assessment read, referral create/read, consent and processing-authority read | Cannot access unassigned cases or administer roles/resources |
| SUPERVISOR | Operator surface plus review/approve/transition and break-glass request capability | Elevation still requires separate approval, scope, expiry, reason, and audit |
| CASE_OFFICER | Assigned-case investigation, review, referral transition/create, consent/authorization read | Cannot access unassigned cases |
| COUNSELLOR / LEGAL_SUPPORT / MEDICAL_SUPPORT | Assigned referral read, safe contact read, outcome read/verify | No general case browsing; referral assignment is mandatory |
| DISTRICT_OFFICER | Scoped summary/sensitive case and assessment/referral/outcome read, audit read, break-glass capability | No transcript/contact permission by default |
| STATE_ADMIN | Scoped summary, assessment, referral/outcome, audit read | No transcript/contact permission by default |
| MINISTRY_ADMIN | Summary, referral/outcome, audit read | No transcript/contact permission by default |
| AUDITOR | Audit, consent, and processing-authorization metadata read | No raw transcript, contact, or case-content read |
| SYSTEM_ADMIN | Actor, role, and resource administration | No case-content permission |

Unknown actions and roles are denied. Adding a new action requires a registry entry, policy review, projection decision, audit decision, and adversarial tests.
