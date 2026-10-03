# SAMBAL Product Specification — 13-Perspective Adversarial Review

> **Packet ID:** PKT-02  
> **Status:** AUTHORITATIVE AUDIT REPORT  
> **Last Updated:** 2026-10-03  
> **Mandate:** Comprehensive Adversarial Scrutiny across 13 Distinct Stakeholder & Vulnerability Perspectives  

---

## 1. Executive Summary & Review Protocol

To ensure that the Packet 02 specification does not reflect insular engineering assumptions, the product, safety, and service architecture was subjected to rigorous adversarial evaluation across 13 distinct human perspectives.

For each perspective, the review identifies:
1. **Primary Human Concerns:** Core anxieties and friction points.
2. **Critical Failure Modes:** Disastrous outcomes if the system fails.
3. **Changes Required & Incorporated:** Concrete specifications enacted in Packet 02 to resolve the failure modes.
4. **Remaining Residual Risks:** Known operational boundaries requiring downstream packet vigilance.

---

## 2. Detailed Perspective Evaluations

### Perspective 1: The Victim / Complainant
- **Concerns:** Fear that calling the helpline will notify the dominant caste perpetrators; fear of being disbelieved, humiliated, or pressured into a compromise; terror that police will arrest them instead.
- **Failure Modes:** Automated dispatch sends local police to the house while perpetrators are watching; cold algorithmic language feels like an interrogation; forced disclosure of traumatic details causes acute panic.
- **Changes Incorporated in Packet 02:**
  - Strict prohibition on automated emergency dispatch; police handoff requires explicit supervisor authorization and citizen consent (`HUMAN_OVERSIGHT.md`).
  - Civic Calm design standards: No red badges, no accusatory copy, non-forced disclosures (`TRAUMA_INFORMED_UX.md`, `CONTENT_GUIDE.md`).
  - Granular consent model allowing citizen to choose who sees their data (`CONSENT_MODEL.md`).
- **Remaining Risk:** Physical intimidation outside the digital system cannot be completely prevented without local witness protection enforcement.

---

### Perspective 2: Low-Literacy Citizen
- **Concerns:** Inability to read complex English/Hindi text forms; fear of making mistakes on dropdowns; humiliation of being excluded by written portals.
- **Failure Modes:** Complex multi-step forms cause abandonment; citizen enters incorrect dates or names due to confusing UI; system rejects spoken dialect as "invalid input".
- **Changes Incorporated in Packet 02:**
  - Voice-first intake channel (`SPEAK`) with native Indic dialect tolerance (`JOURNEYS.md`).
  - Spoken audio explanations for all consent checks (`CONSENT_MODEL.md`).
  - Minimalistic visual cues with generous iconography and plain-language labels (`TRAUMA_INFORMED_UX.md`).
- **Remaining Risk:** Ambient noise on cheap feature phones degrades ASR, requiring operator fallback.

---

### Perspective 3: Silent-Distress User (Trapped / Under Surveillance)
- **Concerns:** An abuser or hostile employer is in the same room; making any noise or having a police website visible on the phone will trigger severe physical battery.
- **Failure Modes:** Helpline places an automatic voice callback, ringing loudly in the room; browser leaves visible history of "Atrocity Complaint"; website emits a chime or audio prompt.
- **Changes Incorporated in Packet 02:**
  - Complete audio suppression in Silent Mode: Zero TTS, zero sound effects (`TRAUMA_INFORMED_UX.md`).
  - Disguised tab title (*"Government Services Portal"*) and neutral emblem icon.
  - Persistent `< 50ms` Quick Exit button (`ESC` key) redirecting to `india.gov.in` and purging session cache.
  - Strict rule forbidding voice callbacks to silent intake users (`JOURNEYS.md`).
- **Remaining Risk:** Physical device inspection by an abuser who monitors cellular carrier SMS logs (mitigated by advising anonymous web chat).

---

### Perspective 4: Frontline Helpline Operator (14566 Triage Agent)
- **Concerns:** Cognitive saturation from 100+ daily crisis calls; fear of being penalized for overriding AI; confusion caused by conflicting model outputs; emotional burnout.
- **Failure Modes:** Red banner alert fatigue leads to operator ignoring true suicide warnings; operator blindly accepts inaccurate AI legal labels due to time quotas.
- **Changes Incorporated in Packet 02:**
  - Three-tier alert hierarchy: Only active violence/suicide triggers audio-visual interrupts (< 3% of calls) (`POLICY_REGISTRY.md`).
  - One-click non-destructive override model with 8 structured reason codes, giving operators full legal empowerment to overrule AI (`HUMAN_OVERSIGHT.md`).
  - Clear 3-second visual triage separating Immediate Safety, SVI, and Incident Urgency (`ASSESSMENT_MODEL.md`).
- **Remaining Risk:** Cumulative vicarious trauma requires institutional mental health debriefs for operators.

---

### Perspective 5: Licensed Counsellor / Mental Health Professional (Tele-MANAS)
- **Concerns:** Receiving unstructured legal grievance dumps; citizen being forced to repeat their trauma; lack of context on acute suicide risk.
- **Failure Modes:** Counsellor unaware of victim's acute suicide attempt during referral; client feels alienated because counsellor asks for facts already given to the helpline.
- **Changes Incorporated in Packet 02:**
  - Role-scoped Counsellor Safe Handoff Packet: Delivers consented psychosocial summary, coping needs, and Immediate Safety State without irrelevant FIR/property litigation records (`SAFE_HANDOFF.md`).
  - Never-Repeat-My-Story memory layer enabling the counsellor to verify prior facts rather than re-interrogate the victim.
  - Clear non-diagnostic boundary: AI never stamps clinical labels (`SELF_HARM_SAFETY_POLICY.md`).
- **Remaining Risk:** Real-time telephony transfer depends on Tele-MANAS regional cell agent availability.

---

### Perspective 6: Legal Aid Advocate (NALSA / DLSA Panel Lawyer)
- **Concerns:** Missing crucial statutory facts needed to oppose bail or file under PoA Section 3; lack of clarity on whether an FIR was actually registered; missing witness names.
- **Failure Modes:** Incomplete referral lacks date/place of incident; advocate receives inadmissible emotional voice telemetry; delay causes expiry of statutory relief windows.
- **Changes Incorporated in Packet 02:**
  - Structured Atrocity Fact Dossier extracting specific statutory entities: incident date, public view status, accused identities, FIR refusal status, PoA Rule 12 relief needs (`SAFE_HANDOFF.md`).
  - Automatic exclusion of private psychological therapy notes to preserve advocate-client privilege and prevent evidentiary contamination.
  - Integration with NALSA 15100 legal aid statutory rights under Section 12(b) of LSA Act (`SERVICE_TAXONOMY.md`).
- **Remaining Risk:** Court scheduling delays in local Special Courts outside the software boundary.

---

### Perspective 7: District Nodal Officer / District Magistrate
- **Concerns:** Public disorder / caste riots; non-compliance with mandatory 7-day relief disbursement under PoA Rule 12(4); lack of visibility into local atrocity hotspots.
- **Failure Modes:** Atrocity complaint gets buried in general grievance queues; delayed witness protection leads to key eyewitness being intimidated and turning hostile.
- **Changes Incorporated in Packet 02:**
  - Clear separation of Reported Incident Urgency, highlighting physical atrocities within 24–48 hours for immediate executive review (`REPORTED_INCIDENT_URGENCY.md`).
  - Formal Threat Assessment Dossier generation for the District Witness Protection Committee under Witness Protection Scheme, 2018 (`SERVICE_TAXONOMY.md`, `SOURCE_REGISTRY.md`).
  - Automated tracking of PoA Rule 12(4) relief compliance deadlines (`METRICS_DICTIONARY.md`).
- **Remaining Risk:** Inter-departmental coordination friction between police and revenue departments.

---

### Perspective 8: Ministry Administrator (MoSJE / DoSJE Central Leadership)
- **Concerns:** Parliamentary accountability; ensuring Union budget reaches intended beneficiaries; proving NHAA 14566 actually delivers relief rather than just logging tickets.
- **Failure Modes:** Reliance on vanity metrics ("10,000 calls processed") masking that 80% of victims never received legal aid or compensation; data breaches leaking victim lists.
- **Changes Incorporated in Packet 02:**
  - Authoritative 7-tier Verified Support Hierarchy answering "Did support actually arrive?" (`REFERRAL_STATE_MACHINE.md`).
  - Ban on calling recommendations "outcomes" in reporting (`REFERRAL_STATE_MACHINE.md`).
  - Disaggregated district gap analytics to allocate mobile legal and psychiatric vans (`RESOURCE_ROUTING_POLICY.md`).
- **Remaining Risk:** Periodic administrative turnover requiring institutionalized onboarding.

---

### Perspective 9: Data Protection & Privacy Officer (DPDP Act Compliance)
- **Concerns:** Violation of DPDP Act 2023 principles; illegal consent bundling; persistent voice recordings creating mass surveillance risks; unencrypted PII in logs.
- **Failure Modes:** Complainant data shared with third-party NGOs without consent; raw audio intercepted or subpoenaed without justification; staff viewing unredacted phone numbers.
- **Changes Incorporated in Packet 02:**
  - 7 granular, unbundled consent dimensions; service delivery strictly unbundled from research consent (`CONSENT_MODEL.md`).
  - Ephemeral raw audio processing: In-memory streaming analysis with zero default disk persistence (`DATA_MINIMIZATION.md`).
  - Role-based data minimization per handoff target (`SAFE_HANDOFF.md`).
  - Strict PII redaction policy in structured application logs (`docs/results/01R-result.md`, `backend/app/logging.py`).
- **Remaining Risk:** Insider operator misbehavior (mitigated by strict role-based access control and immutable audit trails in Packet 04).

---

### Perspective 10: Security Engineer & DevSecOps Lead
- **Concerns:** SQL injection, unauthorized API access, prompt injection in LLM summarizers, DDoS attacks on emergency endpoints, credential leakage.
- **Failure Modes:** Malicious actor injects prompt overrides into complaint text to alter urgency; attacker exfiltrates victim directory via insecure endpoints.
- **Changes Incorporated in Packet 02:**
  - Strict decoupling of safety rules from generative LLMs: High-priority triage relies on deterministic regex and validated models (`POLICY_REGISTRY.md`, `ASSESSMENT_MODEL.md`).
  - Zero raw exception or connection string leakage in health or error responses (`RFC 7807` standard from Packet 01R).
  - Pinned container base images and immutable lockfiles (`uv.lock`, `package-lock.json`).
- **Remaining Risk:** Distributed denial-of-service on public telephony gateway (mitigated by network rate limiters in Packet 06).

---

### Perspective 11: Responsible AI Researcher & Ethicist
- **Concerns:** Algorithmic bias against regional dialects; pseudo-scientific Emotion AI claims; opaque SVI weighting; lack of model abstention under uncertainty.
- **Failure Modes:** Model assigns high risk to innocent speakers due to vocal pitch; system forces high confidence on noisy 8kHz telephone audio; arbitrary linear scoring formulas.
- **Changes Incorporated in Packet 02:**
  - Affective signals classified as `SUPPORTING_SIGNAL_ONLY` with explicit prohibitions against legal or emergency dispatch determinations (`AFFECTIVE_SIGNAL_POLICY.md`).
  - SVI classified as `PROVISIONAL_TRIAGE_POLICY` with zero hardcoded linear arithmetic in Packet 02 (`SVI_POLICY.md`).
  - Explicit uncertainty states (`LOW_AUDIO_QUALITY`, `LANGUAGE_UNCERTAIN`) forcing model abstention and human escalation (`packages/contracts/src/index.ts`).
  - Evidence Precedence Hierarchy: Semantic facts always override acoustic calm (`ASSESSMENT_MODEL.md`).
- **Remaining Risk:** Inherent variance in open-source multilingual ASR checkpoints (benchmarked in Packet 08).

---

### Perspective 12: Accessibility Specialist (A11y Lead)
- **Concerns:** Interfaces inaccessible to blind, deaf, motor-impaired, or cognitively impaired citizens; violation of GIGW 3.0 and WCAG 2.1 AA.
- **Failure Modes:** Screen readers unable to navigate silent intake; color contrast failure on mobile screens in direct sunlight; timeout disconnects users with motor disabilities.
- **Changes Incorporated in Packet 02:**
  - Multi-channel equivalence: Every action achievable via voice, typed text, or single-tap (`JOURNEYS.md`).
  - Strict WCAG 2.1 AA color contrast tokens (minimum 4.5:1 for body, 14.2:1 for primary text) (`TRAUMA_INFORMED_UX.md`).
  - Zero session timeout disconnects during active form completion; automated draft preservation (`JOURNEYS.md`).
- **Remaining Risk:** Screen reader voice synthesis must support regional Indic pronunciation (addressed in Packet 05).

---

### Perspective 13: The Smart India Hackathon (SIH) Evaluator / Judge
- **Concerns:** Is this just another generic ChatGPT wrapper? Does it actually solve SIH26093? Can it run offline? How do they justify emotion AI? Is anything faked?
- **Failure Modes:** Team makes ungrounded claims ("99% emotion accuracy"); demo crashes when internet drops; team cannot explain how Tele-MANAS or NALSA connects.
- **Changes Incorporated in Packet 02:**
  - 19 evidence-backed answers in the Judge Defense Matrix (`JUDGE_DEFENSE_MATRIX.md`).
  - Absolute truth-state tracking: No fake `LIVE` badges; clear distinction between `BASELINE_CANDIDATE`, `SPECIFIED`, and `ADAPTER_READY` (`CAPABILITY_STATUS.md`).
  - Offline Degraded Mode resilience proving core safety functions run without cloud AI (`GOLDEN_SCENARIOS.md` Scenario H).
  - Clear demonstration of how SVI separates from Incident Urgency in Golden Scenarios A and B.
- **Remaining Risk:** Time constraints during live 3-minute pitch (mitigated by scripted golden demo walkthroughs in Packet 24).
