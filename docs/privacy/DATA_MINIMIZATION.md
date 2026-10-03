# SAMBAL Privacy Specification — Data Minimization & Raw Audio Policy

> **Packet ID:** PKT-02  
> **Status:** AUTHORITATIVE SPECIFICATION  
> **Last Updated:** 2026-10-03  
> **Traceability:** DPDP Act 2023 Data Minimization Principles, MinIO Storage Architecture  

---

## 1. Principle of Strict Data Minimization

The collection of personal data in high-stakes public safety systems must follow the principle of **Proportional Necessity**:
> **No data field shall be collected, requested, or stored merely because "it might be useful later."**  
> Every single field in the data architecture must have an explicit, statutory, or operational justification.

---

## 2. Workflow-Specific Data Minimization Registry

| Workflow / Surface | Minimum Data Required | Permitted Optional Data | Strictly Prohibited / Unnecessary Data | Sharing Scope | Retention Boundary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Initial Citizen Ingestion (PWA/IVR)** | Spoken or typed grievance statement; preferred language; basic incident location (district). | Contact phone number (optional if anonymous tracking selected); safe callback time. | National identity numbers (Aadhaar), biometric data, bank details, caste certificate numbers. | Ingestion layer only (never public). | Purged from browser storage upon submission or Quick Exit. |
| **Silent Distress Intake** | Tapped emergency answers (safe/unsafe, immediate help needed); approximate location. | Silent SMS number. | Detailed written narrative; background voice audio; browser device fingerprints. | Operator Triage Queue only. | In-memory session purged; dossier minimized. |
| **Helpline Operator Triage** | Validated transcript; incident date & location; identified needs; immediate safety flag. | Caller name (if voluntarily disclosed); specific landmark. | Full family ancestry, income tax details, unrelated civil litigation history. | Internal Triage Hub (Operator + Supervisor). | Case lifecycle duration (PoA statutory record). |
| **Legal Aid Referral (NALSA)** | Date, time, village of incident; nature of offence; accused names; police FIR status. | Complainant phone number (for advocate consultation); witness names. | Medical therapy notes, psychological distress scores, raw acoustic telemetry. | Assigned DLSA / TLSC Panel Advocate. | Governed by Legal Services Authorities Act record rules. |
| **Mental Health Referral (Tele-MANAS)** | Preferred language; psychosocial distress summary; safe contact number; immediate safety state. | Complainant first name; preferred callback window. | Full legal dispute filings, property documents, accused criminal records. | Assigned Tele-MANAS Cell Counsellor. | Governed by Mental Healthcare Act 2017 & Tele-MANAS protocol. |
| **Emergency Rescue (ERSS 112)** | Immediate physical danger description; precise current location / address; phone number. | Number of trapped individuals. | Historical complaints; detailed legal claims; mental health session logs. | ERSS 112 Control Room Dispatcher. | Governed by ERSS emergency log retention policies. |

---

## 3. Authoritative Raw Audio Policy

Voice recordings of citizens reporting atrocities contain extreme emotional vulnerability, ambient background sounds, intimate conversations, and sensitive identifying details. Persisting raw audio on disk creates a severe data breach and surveillance liability.

### 3.1 The Default Architecture: Ephemeral Streaming Processing
```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ DEFAULT OPERATIONAL DOCTRINE:                                               │
│                                                                             │
│                  PROCESS TRANSIENTLY IN VOLATILE MEMORY                     │
│                                                                             │
│                       DO NOT RETAIN BY DEFAULT                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **In-Memory Buffering:** Audio streams are received as discrete chunks (PCM / WAV) in volatile memory buffers strictly for the duration of real-time ASR transcription and acoustic feature extraction.
2. **Immediate Volatile Deletion:** Once a transcription segment is finalized by the ASR engine, the corresponding raw audio chunk is expunged from memory.
3. **Zero Default Disk Persistence:** Neither the web server, nor the backend API, nor the MinIO object storage writes raw audio files to disk by default.

---

### 3.2 Strict Conditions for Authorized Raw Audio Retention

Raw audio retention is permitted ONLY when the following four conditions are simultaneously satisfied:

```mermaid
graph TD
    Condition1[1. Explicit Unbundled Citizen Opt-In Consent] --> Gate{All 4 Met?}
    Condition2[2. Formal Legal Evidence Request under PoA Act] --> Gate
    Condition3[3. AES-256-GCM Envelope Encryption] --> Gate
    Condition4[4. Automated Cryptographic Deletion Timer] --> Gate
    
    Gate -->|YES| MinIOStorage[Encrypted MinIO S3 Audio Bucket]
    Gate -->|NO| EphemeralPurge[Immediate In-Memory Purge]
```

1. **Condition 1: Explicit Unbundled Consent:** The complainant has explicitly toggled the separate raw audio retention consent option, after hearing a plain-language explanation of its purpose.
2. **Condition 2: Statutory Evidentiary Purpose:** The recording is requested as formal electronic evidence under Section 65B of the Indian Evidence Act / Section 63 of Bharatiya Sakshya Adhiniyam (BSA) for an active Special Court atrocity trial.
3. **Condition 3: End-to-End Cryptographic Protection:**
   - Audio is encrypted before writing to MinIO using **AES-256-GCM** with a per-recording Data Encryption Key (DEK).
   - Encryption keys are stored in a dedicated Hardware Security Module (HSM) / Key Management Service (KMS) with restricted role-based decryption.
4. **Condition 4: Automated Deletion Lifecycle:**
   - Every stored audio file possesses an immutable metadata tag: `ExpirationTimestamp`.
   - MinIO bucket lifecycle policies automatically delete the object and purge all underlying storage blocks when the retention period expires.
   - *Authoritative Duration Doctrine:* The platform does NOT invent an arbitrary duration (such as "30 days" or "1 year"). The retention duration is tied strictly to official statutory rules:
     - Pre-FIR Investigation Buffer: 90 days (aligned with statutory chargesheet filing limits under CrPC/BNSS).
     - Trial Record: Maintained only if formally requisitioned by the Special Court.
     - Unrequisitioned recordings are permanently deleted upon investigation closure.
