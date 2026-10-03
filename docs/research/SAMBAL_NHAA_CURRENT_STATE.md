# SAMBAL & NHAA Current State Analysis & Integration Mapping

> **Document ID:** GOV-ECOSYSTEM-CURRENT-STATE-V2  
> **Topic:** Ministry of Social Justice & Empowerment (MoSJE) — National Helpline Against Atrocities (NHAA - 14566) & SAMBAL Framework  
> **Research Date:** October 2026  
> **Classification:** Official Public-Sector Architecture & Operational Audit

---

## 1. Executive Summary & Official Identity

The **National Helpline Against Atrocities (NHAA)** was formally launched by the Ministry of Social Justice and Empowerment (MoSJE), Department of Social Justice and Empowerment (DoSJE), Government of India, to ensure the rigorous implementation of:
- **The Protection of Civil Rights Act, 1955 (PCR Act)**
- **The Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989 (PoA Act)**

### Official Access Channels
- **Short Code:** `14566` (Toll-free across all telecom service providers in India).
- **Alternate Toll-Free Number:** `1800-202-1989`.
- **Operational Availability:** 24 hours a day, 7 days a week, 365 days a year.
- **Languages:** Available in Hindi, English, and regional languages mapped to State/UT operational zones.
- **Web Portal:** Official self-service docket generation and tracking portal.
- **Mobile Channel:** Android and web-based applications for case submission.
- **Framework Transition:** The initiative is increasingly unified under the **SAMBAL** umbrella (Strengthening Access to Grievance Redressal / Central Sector Scheme for PCR & PoA implementation).

---

## 2. Current Operating Model of NHAA (14566)

The current operational lifecycle of a grievance or atrocity complaint follows a traditional administrative ticketing workflow:

```text
[ Citizen / Complainant ]
          │ (Dials 14566 / Web Form)
          ▼
[ Central IVRS & Call Router ]
          │ (Select Language)
          ▼
[ Helpline Operator Desk ]
          │ (Manual phone interview & keyboard data entry)
          ▼
[ NHAA Docket CRM Engine ]
          │ (Generates Docket ID; sends SMS confirmation)
          ▼
[ Administrative Redirection ]
          ├──► District Magistrate (DM) / Collector
          ├──► Superintendent of Police (SP) / Special Cell
          └──► District Social Welfare Officer
          │
[ Periodic Manual Review & Police Investigation (Target: 60 Days) ]
```

### Empirical Deficits in the Current Workflow
1. **Unstructured Emotional Triage:** Helpline operators are primarily trained as call-centre customer service representatives or clerical data-entry staff. They are not clinical trauma specialists. When a caller experiences acute panic, dissociation, or suicidal ideation, operators have no real-time decision-support tools.
2. **Failure to Detect Covert Intimidation:** A caller forced to speak in the presence of an oppressor, or speaking in a calm, flat, dissociated voice about imminent murder threats, is often assigned low administrative priority because they did not "sound hysterical."
3. **Siloed Helplines & Broken Handoffs:** If a victim requires urgent psychiatric intervention, the operator can at best recite the number for Tele-MANAS (`14416`). The victim is left to dial another number, face another IVR, and recount their horrific experience from scratch.
4. **No Closed-Loop Verification:** The helpline software marks a case as "Referred to Legal Aid" as soon as a docket is forwarded. It possesses zero telemetry to answer: *Did the victim meet a lawyer? Did they receive witness protection? Did mental health support actually commence?*

---

## 3. The SAMBAL Intelligence & Response Layer Architecture

Our product does not attempt to replace or rebuild the administrative core of NHAA. Building another redundant grievance portal would violate government procurement realities. 

Instead, **SAMBAL Intelligence & Response Layer** is architected as a **Headless Cognitive Co-Pilot and Response Orchestration Layer** that seamlessly sits between the incoming communication streams and the backend administrative systems.

```text
                                  CITIZEN CHANNELS
              [ 14566 Telephony ]  [ SAMBAL Portal ]  [ Silent PWA Flow ]
                       │                  │                   │
                       └──────────────────┼───────────────────┘
                                          │
                                          ▼
                         SAMBAL CHANNEL & CONSENT GATEWAY
                                          │
                         ┌────────────────┴────────────────┐
                         ▼                                 ▼
              [ Real-Time Stream Ingest ]        [ Consent & Privacy Vault ]
                         │                                 │
                         ▼                                 ▼
          SAMBAL HEADLESS INTELLIGENCE ENGINE     DPDP Minimization & Audit
          ├── Multilingual ASR (Indic)
          ├── Speech & Acoustic Analytics (F0, pauses, rate)
          ├── Affective Distress Signal Engine
          ├── Text Safety & Intimidation NLP
          ├── Deterministic Self-Harm Safety Gate
          └── Multimodal Evidence Fusion (SVI 0-100)
                         │
                         ├─────────────────────────────────┐
                         ▼                                 ▼
             [ NHAA Operator Co-Pilot ]       [ Three-Dimensional Triage ]
             • Live Transcript & Markers      • Immediate Safety Gate
             • Evidence Inspector             • SVI Risk Band (Low-Crit)
             • Suggested Trauma Questions     • Statutory Incident Urgency
             • Human Oversight & Override                  │
                         │                                 │
                         └────────────────┬────────────────┘
                                          │
                                          ▼
                      RESOURCE & CLOSED-LOOP ORCHESTRATOR
                                          │
         ┌───────────────────┬────────────┴───────┬───────────────────┐
         ▼                   ▼                    ▼                   ▼
   [ Tele-MANAS ]      [ NALSA / DLSA ]    [ Police / ERSS 112 ] [ One-Stop / OSC ]
   (Mental Health)      (Legal Aid)        (Urgent Protection)   (Shelter/Med)
         │                   │                    │                   │
         └───────────────────┼────────────────────┴───────────────────┘
                             ▼
              CLOSED-LOOP REFERRAL LIFECYCLE
              (Referred → Acknowledged → Contacted → Support Started → Verified Outcome)
```

---

## 4. Integration Reality & Realistic API Strategy

### Golden Rule: No Fabricated APIs
Government departments (MoSJE, MoHFW, Ministry of Home Affairs) do not offer open, public, unauthenticated REST APIs for production helplines. Attempting to present mock HTTP calls as "official live government endpoints" is technically fraudulent and will be rejected by discerning judges.

### Three-Tiered Adapter Architecture
To maintain absolute architectural credibility, our platform implements canonical adapter abstractions with explicit status definitions:

1. **`LIVE`:** Tested, functional local services and verified public endpoints (e.g., local AI4Bharat/Whisper ASR, local openSMILE/librosa feature extractors, live DB, WebSockets).
2. **`SANDBOX`:** Production-grade simulation of external agency endpoints (e.g., mock Tele-MANAS intake webhook, simulated NALSA legal-aid referral docket API, simulated District Police Atrocity Cell feed) with full error injection, latency simulation, and cryptographic signature validation.
3. **`ADAPTER_READY`:** Clean, typed interfaces documented with OpenAPI 3.1 and JSON schemas ready to connect to NIC (National Informatics Centre) / MoSJE enterprise gateways the moment official security clearance and VPN credentials are provided.

### Canonical Government Integration Contracts
- **`SAMBALCaseAdapter`:** Ingests external docket IDs; synchronizes complaint status, FIR details, and district assignment.
- **`TeleManasAdapter`:** Packages consented psychiatric referral packages (safe handoff) and receives bi-directional consultation acknowledgements.
- **`LegalAidAdapter`:** Transmits statutory legal-aid eligibility notices under PoA Act Section 15A (Rights of Victims and Witnesses).
- **`ERSS112Adapter`:** High-priority dispatch trigger when Immediate Safety Gate detects active life-threatening violence.
