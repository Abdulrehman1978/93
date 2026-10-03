# Indian Support & Protection Ecosystem Integration Mapping

> **Document ID:** SUPPORT-ECOSYSTEM-MAPPING-V2  
> **Topic:** Operational & Statutory Support Ecosystem for Atrocity Victims in India  
> **Applicable Acts:** PCR Act 1955, PoA Act 1989 (Amended 2015/2018), LSA Act 1987, Mental Healthcare Act 2017  
> **Date:** October 2026

---

## 1. Overview of the Support Ecosystem

When an individual contacts **NHAA (14566)**, their needs frequently transcend standard administrative complaint logging. A victim of a caste-based atrocity typically requires coordinated multi-agency assistance across four distinct domains:
1. **Psychological & Trauma Support**
2. **Statutory Free Legal Aid & Representation**
3. **Emergency Physical Protection & Law Enforcement**
4. **Socio-Economic Relief, Medical Care & Shelter**

The SAMBAL Intelligence Layer provides the missing connective tissue, orchestrating closed-loop handoffs without forcing victims to recount traumatic narratives across disconnected government offices.

---

## 2. Institutional Actors & Integration Architecture

```text
                               SAMBAL RESPONSE ORCHESTRATOR
                                            │
        ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
        ▼                   ▼                               ▼                   ▼
 [ Tele-MANAS 14416 ] [ NALSA / DLSA ]             [ ERSS 112 / Police ] [ OSC Sakhi / Relief ]
  (Mental Health)      (Legal Aid)                  (Urgent Safety)       (Shelter & Compensation)
  - Tier 1 Counsellor  - Free Advocate (LSA Sec 12) - Emergency Dispatch  - Medical Examination
  - Tier 2 Specialist  - Sec 15A Witness Protection - Atrocity Cell DSP   - Emergency Shelter Stay
  - Trauma Protocol    - Bail Hearing Objections    - Protection Escort   - PoA Statutory Relief
```

### Agency 1: Tele-MANAS (14416 / 1800-891-4416)
- **Ministry:** Ministry of Health & Family Welfare (MoHFW) | **Nodal Institute:** NIMHANS.
- **Network:** 51 Tele-MANAS cells operating across all States and UTs in 20+ regional languages.
- **Two-Tier Architecture:**
  - *Tier 1:* 24/7 dedicated call centers staffed by qualified counselors and clinical psychologists.
  - *Tier 2:* Direct physical escalation to District Mental Health Programme (DMHP) medical officers and psychiatrists at district hospitals.
- **Integration Mechanism (`TeleManasAdapter`):**
  - **State:** `SANDBOX` / `ADAPTER_READY`.
  - Transmits a structured, consented **Safe Handoff Package** containing: primary distress indicators, preferred language, verified contact number, and non-retraumatizing incident summary.
  - Receives bi-directional webhook callbacks on referral acknowledgement, scheduled counseling appointments, and clinical outcome codes.

### Agency 2: Legal Services Authorities (NALSA / SLSA / DLSA)
- **Statutory Mandate:** Legal Services Authorities Act, 1987 (LSA Act) read with Section 15A of the PoA Act.
- **Legal Right:** Under Section 12(b) of the LSA Act, **every member of a Scheduled Caste or Scheduled Tribe is unconditionally entitled to free legal aid**, regardless of income.
- **PoA Section 15A Protections:**
  - Right to be heard at all court proceedings including bail applications.
  - Protection against intimidation, coercion, and violence.
  - Mandatory provision of free advocates by the State.
  - Reimbursement for travel, maintenance, and food expenses during trials.
- **Integration Mechanism (`LegalAidAdapter`):**
  - Pre-populates the NALSA legal aid application format with verified PoA docket information and transmits it to the relevant District Legal Services Authority (DLSA) Front Office.

### Agency 3: Emergency Response Support System (ERSS - 112)
- **Ministry:** Ministry of Home Affairs (MHA).
- **Function:** Single unified pan-India emergency number for immediate police dispatch, ambulance, and fire services.
- **Integration Mechanism (`ERSS112Adapter`):**
  - Triggered exclusively when the **Immediate Safety Gate** detects active violence, physical assault in progress, or armed hostage/siege situations.
  - Requires explicit human operator authorization before emergency payload dispatch to avoid accidental police deployment.

### Agency 4: One-Stop Centres (OSC - Sakhi) & PoA District Welfare
- **Ministry:** Ministry of Women & Child Development (MoWCD) & MoSJE.
- **Function:** Provides integrated shelter, medical examination, counseling, and legal assistance under one roof for women and children facing violence.
- **Statutory Economic Relief:** Under Rule 11 & Rule 12 of PoA Rules (Annexure I), atrocity victims are entitled to immediate cash relief (ranging from ₹1,00,000 to ₹8,25,000 depending on the nature of the offence) deposited directly into their bank accounts within 7 days of FIR registration.
- **Integration Mechanism (`ReliefRehabAdapter`):**
  - Alerts the District Social Welfare Officer and SDM to initiate mandatory statutory compensation without bureaucratic delays.

---

## 3. The Closed-Loop Referral Lifecycle State Machine

A referral is not a passive email notification. It is an actively tracked state machine:

```text
[ RECOMMENDED ]
       │ (AI identifies need based on evidence)
       ▼
[ REVIEW_REQUIRED ]
       │ (Operator evaluates evidence in Live Copilot)
       ├──► [ DECLINED ] (Operator or Complainant rejects referral)
       ▼
[ APPROVED ]
       │ (Complainant provides specific consent to share data)
       ▼
[ REFERRED ]
       │ (Safe Handoff transmitted via Adapter)
       ▼
[ ACKNOWLEDGED ] ◄── SLA Alert if > 2 hours for Critical, > 12 hours for High
       │ (Receiving agency confirms receipt and assigns worker)
       ▼
[ CONTACT_PENDING ]
       │
       ▼
[ CONTACTED ]
       │ (Support agency establishes contact with victim)
       ▼
[ APPOINTMENT_SCHEDULED ]
       │
       ▼
[ SERVICE_STARTED ]
       │ (Counseling / Legal representation active)
       ▼
[ FOLLOW_UP_DUE ] ◄── System prompts SAMBAL operator after 7 / 14 days
       │
       ▼
[ COMPLETED / OUTCOME_LOGGED ] ◄── Verified support delivered
```

### Addressing the Fundamental Failure Mode: "Did Help Actually Arrive?"
By enforcing state transitions with automated SLA escalations, the platform detects when referrals stall (e.g., a victim was referred to DLSA 5 days ago but no lawyer has contacted them). The system surfaces these stalls to the **Supervisor Operations Hub**, enabling targeted institutional intervention.
