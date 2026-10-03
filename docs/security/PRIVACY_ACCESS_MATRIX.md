# Packet 04 Privacy and Access Matrix

| Data surface | Operator | Supervisor / officer | Provider | Auditor | System admin |
| --- | --- | --- | --- | --- | --- |
| Case summary | Assigned case only | Policy/org/jurisdiction scope | No general access | No | No |
| Transcript / translation | Assigned case + purpose authorization | Scoped + purpose authorization | No | No | No |
| Subject contact | Assigned case + purpose authorization | Scoped + purpose authorization | Assigned referral safe-contact projection only | No | No |
| Assessment/evidence pointers | Assigned/scoped case + purpose authorization | Scoped + purpose authorization | No general access | No raw content | No |
| Referral safe handoff | Create/read within case | Approve/transition in scope | Assigned referral only | Metadata only | No case content |
| Consent / processing authorization | Read/record per role and purpose | Manage in scope | No | Metadata read | No |
| Audit metadata | Limited operational need | Scoped operational need | No raw content | Security audit surface | Administration only |

Sensitive access requires an exact active processing purpose. Purpose authorization is not a role and consent is not silently substituted for lawful processing authority. All decisions are logged with actor, action, object, purpose, policy version, correlation ID, and safe reason code.
