# SAMBAL Source Registry — Verified Official Public Service Baselines

> **Packet ID:** PKT-02  
> **Status:** AUTHORITATIVE REGISTRY  
> **Last Verified At:** 2026-10-03  
> **Traceability:** SIH26093 Government Integrations, Official Public Services  

---

## 1. Executive Summary & Verification Standard

In compliance with the project's strict truth-state doctrine, every external public institution, emergency service, and statutory helpline referenced by SAMBAL must have an authenticated record in this **Source Registry**.

No integration may claim `LIVE` status unless real production credentials, authenticated peering, or direct physical handoffs exist. All other services are tracked truthfully as `ADAPTER_READY` or `SANDBOX`.

---

## 2. Directory of Official Public Service Baselines

### Registry Entry 1: Emergency Response Support System (ERSS 112)
- **Official Name:** Emergency Response Support System (ERSS)
- **Nodal Ministry:** Ministry of Home Affairs (MHA), Government of India
- **National Baseline Helpline:** `112` (Unified Pan-India Emergency Number)
- **Statutory / Administrative Mandate:** Integration of Police (100), Fire (101), Health/Ambulance (102), and Women Helpline (1090) under the National Emergency Response Framework.
- **Coverage:** All 36 States and Union Territories.
- **Channels Supported:** Voice (112), SMS, 112 India Mobile App, Web Portal.
- **SAMBAL Integration Pattern:** `HUMAN_AUTHORIZED_EMERGENCY_HANDOFF`
  - System prepares an emergency dispatch dossier (GPS location, threat nature, contact number).
  - Shift supervisor must authenticate the dispatch; zero autonomous algorithmic auto-dialing.
- **Current Truth Status:** `ADAPTER_READY` (Verified public baseline; local mock webhook sandbox).
- **Source Verification URL:** `https://112.gov.in`

---

### Registry Entry 2: Tele Mental Health Assistance and Networking Across States (Tele-MANAS)
- **Official Name:** Tele Mental Health Assistance and Networking Across States (Tele-MANAS)
- **Nodal Ministry:** Ministry of Health and Family Welfare (MoHFW), Government of India
- **Apex Coordinating Institute:** National Institute of Mental Health and Neurosciences (NIMHANS), Bengaluru
- **National Baseline Toll-Free Numbers:** `14416` / `1800-891-4416`
- **Network Scale (As of August 2026 Baseline):** 53 operational Tele-MANAS cells functioning across all 36 States and Union Territories.
- **Linguistic Coverage:** 20 Indian languages supported across specialized regional cells.
- **Tiering Architecture:**
  - *Tier 1:* Frontline trained crisis counsellors and psychiatric social workers.
  - *Tier 2:* Clinical psychologists, psychiatrists, and specialized tertiary mental health institutes (NIMHANS, LGBRIMH Tezpur, CIP Ranchi).
- **SAMBAL Integration Pattern:** `CONSENTED_WARM_TRANSFER & REFERRAL PACKET`
  - Complainant preferred language, distress summary, and immediate safety state transferred upon consent.
- **Current Truth Status:** `ADAPTER_READY` (Verified public baseline; simulated telephony bridge).
- **Source Verification URL:** `https://telemanas.mohfw.gov.in`

---

### Registry Entry 3: National Legal Services Authority (NALSA)
- **Official Name:** National Legal Services Authority (NALSA)
- **Statutory Authority:** Legal Services Authorities Act, 1987 (Act No. 39 of 1987)
- **National Baseline Helpline:** `15100` (National Legal Aid Toll-Free Helpline)
- **Statutory Mandate for SC/ST:** Section 12(b) of the Legal Services Authorities Act, 1987 explicitly provides that a member of a Scheduled Caste or Scheduled Tribe is entitled to free legal services as a matter of statutory right, regardless of income criteria.
- **Institutional Hierarchy:**
  - *Apex Level:* National Legal Services Authority (Supreme Court).
  - *State Level:* State Legal Services Authority (SLSA - High Court).
  - *District Level:* District Legal Services Authority (DLSA - District Court).
  - *Taluka Level:* Taluka Legal Services Committee (TLSC - Sub-divisional Court).
- **SAMBAL Integration Pattern:** `CONSENTED_FACT_DOSSIER_HANDOFF`
  - Routes incident date, accused names, FIR status, and Rule 12 compensation needs directly to the jurisdictional DLSA front office.
- **Current Truth Status:** `STATUTORY_BASELINE_VERIFIED` (Directory-mapped; adapter ready).
- **Source Verification URL:** `https://nalsa.gov.in`

---

### Registry Entry 4: Witness Protection Scheme, 2018
- **Official Title:** Witness Protection Scheme, 2018
- **Legal Authority:** Approved by the Supreme Court of India in *Mahender Chawla & Ors. v. Union of India & Ors. (2019) 14 SCC 615* (held to be the law of the land under Article 141 of the Constitution until statutory enactment).
- **Statutory Complement:** Section 15A of the Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989 (inserted via 2015 Amendment, detailing rights of victims and witnesses).
- **Competent Authority:** **District Witness Protection Committee** (chaired by the District and Sessions Judge, with the District Magistrate and District Superintendent of Police as members).
- **Threat Categorization Framework:**
  - *Category 'A':* Threat extends to life of witness or family members during investigation or trial.
  - *Category 'B':* Threat extends to safety, reputation, or property of witness.
  - *Category 'C':* Threat is moderate (harassment, intimidation).
- **SAMBAL Integration Pattern:** `THREAT_ASSESSMENT_DOSSIER_GENERATION`
  - The system compiles reported intimidation facts, accused bail status, and proximity risks into a formal Threat Assessment Dossier for the District Nodal Officer to place before the District Committee.
  - *Absolute Guardrail:* The system NEVER claims to grant witness protection; it facilitates authorized judicial/administrative application.
- **Current Truth Status:** `LEGAL_FRAMEWORK_VERIFIED`.
- **Source Verification:** Supreme Court of India Judgment *Writ Petition (Criminal) No. 156 of 2016*.

---

### Registry Entry 5: National Helpline Against Atrocities (NHAA 14566)
- **Official Name:** National Helpline Against Atrocities (NHAA)
- **Nodal Ministry:** Ministry of Social Justice and Empowerment (MoSJE), Department of Social Justice and Empowerment (DoSJE)
- **Toll-Free Helpline:** `14566`
- **Mandate:** End-to-end docketing and grievance redressal for victims under the Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989 and Protection of Civil Rights Act, 1955.
- **SAMBAL Integration Pattern:** `CORE_LAYER_AUGMENTATION`
  - SAMBAL acts as the AI-assisted intelligence, triage, and multi-agency referral layer directly augmenting NHAA call-center and portal workflows.
- **Current Truth Status:** `ADAPTER_READY` (Local canonical adapter framework implemented).
- **Source Verification URL:** `https://nhaa.dosje.gov.in`
