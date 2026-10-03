# Packet 03 Entity Relationship Diagrams

The diagrams are split by domain so the safety-critical relationships remain readable. All identifiers are UUIDs unless a field is explicitly a safe external/reference string.

## Governance and case source

```mermaid
erDiagram
    JURISDICTIONS ||--o{ ORGANIZATIONS : scopes
    JURISDICTIONS ||--o{ CASES : scopes
    ORGANIZATIONS ||--o{ CASES : owns
    SUBJECTS ||--o{ SUBJECT_CONTACTS : has
    SUBJECTS ||--o{ CASES : owns
    CASES ||--o{ CASE_PARTICIPANTS : includes
    CASES ||--o{ CASE_STATUS_EVENTS : records
    CASES ||--o{ INTERACTIONS : contains
    INTERACTIONS ||--o{ INTERACTION_EVENTS : records
    INTERACTIONS ||--o{ TRANSCRIPT_SEGMENTS : yields
    TRANSCRIPT_SEGMENTS ||--o{ TRANSLATIONS : represents
```

## Privacy, intelligence, and provenance

```mermaid
erDiagram
    SUBJECTS ||--o{ CONSENT_EVENTS : gives
    CASES ||--o{ CONSENT_EVENTS : scopes
    PROCESSING_PURPOSES ||--o{ CONSENT_EVENTS : governs
    CASES ||--o{ PROCESSING_AUTHORIZATIONS : scopes
    INTERACTIONS ||--o{ PROCESSING_AUTHORIZATIONS : scopes
    PROCESSING_PURPOSES ||--o{ PROCESSING_AUTHORIZATIONS : permits
    PROCESSING_AUTHORITY_TYPES ||--o{ PROCESSING_AUTHORIZATIONS : supplies
    CONSENT_EVENTS ||--o{ PROCESSING_AUTHORIZATIONS : supports
    CASES ||--o{ ASSESSMENTS : receives
    INTERACTIONS ||--o{ ASSESSMENTS : informs
    ASSESSMENTS ||--o{ IMMEDIATE_SAFETY_RESULTS : has
    ASSESSMENTS ||--o{ SVI_RESULTS : has
    ASSESSMENTS ||--o{ INCIDENT_URGENCY_RESULTS : has
    ASSESSMENTS ||--o{ ASSESSMENT_EVIDENCE : references
    ASSESSMENTS ||--o{ ASSESSMENT_REVIEWS : reviewed_by
    MODEL_RUNS ||--o{ IMMEDIATE_SAFETY_RESULTS : provenance
    MODEL_RUNS ||--o{ SVI_RESULTS : provenance
    MODEL_RUNS ||--o{ INCIDENT_URGENCY_RESULTS : provenance
    TRANSCRIPT_SEGMENTS ||--o{ ASSESSMENT_EVIDENCE : source
```

## Support and operations

```mermaid
erDiagram
    CASES ||--o{ REFERRALS : sends
    SERVICE_RESOURCES ||--o{ REFERRALS : selected
    SERVICE_RESOURCES ||--o{ RESOURCE_VERIFICATIONS : verified_by
    PROCESSING_AUTHORIZATIONS ||--o{ REFERRALS : authorizes
    CONSENT_EVENTS ||--o{ REFERRALS : consents
    REFERRALS ||--o{ REFERRAL_EVENTS : evolves
    REFERRALS ||--o{ SUPPORT_OUTCOMES : measures
    FOLLOW_UP_POLICIES ||--o{ FOLLOW_UPS : schedules
    REFERRALS ||--o{ FOLLOW_UPS : receives
    CONTACT_ATTEMPT_POLICIES ||--o{ FOLLOW_UPS : governs
    FOLLOW_UPS ||--o{ CONTACT_ATTEMPTS : records
    CONTACT_ATTEMPT_POLICIES ||--o{ CONTACT_ATTEMPTS : governs
```

## Platform governance

```mermaid
erDiagram
    ASYNC_JOBS {
        uuid id PK
        string job_type
        string payload_reference
        string status
    }
    INTEGRATION_EVENTS {
        uuid id PK
        string provider
        string idempotency_key UK
        string status
    }
    AUDIT_EVENTS {
        uuid id PK
        string entity_type
        string entity_id
        timestamptz occurred_at
    }
    DELETION_REQUESTS {
        uuid id PK
        string object_type
        string object_id
        string state
    }
```
