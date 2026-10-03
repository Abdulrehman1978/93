# SAMBAL Product Specification — SIH Judge Defense Matrix

> **Packet ID:** PKT-02  
> **Status:** AUTHORITATIVE SPECIFICATION  
> **Last Updated:** 2026-10-03  
> **Core Purpose:** Defensible, Evidence-Backed Responses to Technical, Ethical, and Operational Queries  

---

## 1. Executive Summary & Defensibility Doctrine

During SIH evaluations, government reviews, and academic scrutiny, judges will probe the technical integrity, legal boundaries, and ethical safeguards of SAMBAL. Casual claims, ungrounded buzzwords ("99% accuracy", "Emotion AI detects lies"), or evasive answers destroy credibility.

This matrix equips the engineering and product team with rigorous, technically precise answers backed by active repository artifacts, established policies, and strict truth-state tracking.

---

## 2. The 19 Core Judge Questions & Defenses

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. WHY NOT JUST USE CHATGPT OR GEMINI?                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: General-purpose LLMs are ungrounded, non-deterministic, have  │
│ high latency, lack acoustic/telephony speech capabilities, hallucinate legal│
│ authorities, and violate sovereign data residency when handling citizen PII.│
│ Technical Evidence: Packet 00 Lean-Core Architecture; Packet 01 RFC 7807    │
│ problem details; Packet 02 Human Oversight Matrix; deterministic regex &    │
│ acoustic pipelines.                                                         │
│ Demo Surface: Golden Scenario H (LLM Outage Resilience Demo).                │
│ Current Truth Status: ARCHITECTURE_LOCKED.                                  │
│ Limitation: LLMs are utilized strictly for auxiliary summarization and      │
│ structured extraction behind local guardrails, never autonomous triage.     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. CAN VOICE ANALYSIS ACTUALLY DIAGNOSE TRAUMA?                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: NO. Voice analysis CANNOT diagnose trauma, and claiming so is │
│ scientific pseudoscience. Acoustic features (pitch jitter, tremor, pauses)  │
│ merely serve as supporting cues to assist an operator's conversational      │
│ pacing. Diagnostic claims are strictly forbidden by system policy.          │
│ Technical Evidence: docs/product/ASSESSMENT_MODEL.md (Guardrail 4);          │
│ docs/ai/AFFECTIVE_SIGNAL_POLICY.md (SUPPORTING_SIGNAL_ONLY).                │
│ Demo Surface: Evidence Inspector showing acoustic telemetry with explicit   │
│ "SUPPORTING CUE ONLY — NON-DIAGNOSTIC" banner.                              │
│ Current Truth Status: POLICY_ENFORCED.                                      │
│ Limitation: Acoustic cues vary across dialects, age, and respiratory health;│
│ they are strictly secondary to explicit semantic testimony.                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. WHY USE EMOTION AI AT ALL IF IT CANNOT DIAGNOSE?                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: Because high call volumes cause frontline operator cognitive  │
│ fatigue. Non-semantic acoustic signals (e.g. sudden prolonged silence or     │
│ severe vocal tremor) alert the operator to slow down, listen deeper, and    │
│ offer trauma-informed pauses. It enhances operator empathy, not automation. │
│ Technical Evidence: docs/product/TRAUMA_INFORMED_UX.md;                    │
│ backend/app/intelligence/contracts.py (AcousticFeatureProvider).            │
│ Demo Surface: Operator Copilot Workspace displaying pacing recommendations. │
│ Current Truth Status: BASELINE_CANDIDATE.                                   │
│ Limitation: Must never be used to judge credibility or legal urgency.        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. WHAT DOES SVI (STRESS VULNERABILITY INDEX) ACTUALLY MEAN?                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: SVI is a multidimensional triage prioritization band          │
│ (LOW, MODERATE, HIGH, CRITICAL) reflecting cumulative psychological, social,│
│ and institutional vulnerability to order administrative review queues.      │
│ Technical Evidence: packages/contracts/src/index.ts (SVIBandSchema);        │
│ docs/ai/SVI_POLICY.md.                                                      │
│ Demo Surface: Operator Triage Queue showing SVI Bands ordering work.        │
│ Current Truth Status: PROVISIONAL_TRIAGE_POLICY.                            │
│ Limitation: Mathematical fusion formula is unencoded in Packet 02 and will  │
│ be empirically calibrated in Packet 11; no fake arithmetic currently.       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. WHO DECIDED THE SVI WEIGHTS? HOW DO WE KNOW THEY ARE FAIR?               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: No arbitrary weights exist today. Packet 02 explicitly bans   │
│ invented arithmetic (e.g. 0.3*text + 0.2*audio). Weights and thresholds are │
│ deferred to Packet 11, where they will be calibrated against clinical and   │
│ legal expert benchmarks using formal ROC/AUC and fairness parity audits.    │
│ Technical Evidence: docs/ai/SVI_POLICY.md; docs/results/02-result.md.       │
│ Demo Surface: Traceability Matrix showing Packet 11 calibration schedule.   │
│ Current Truth Status: STRICT_DOCTRINE_PRESERVED.                           │
│ Limitation: Any scoring system risks bias; mitigation requires continuous   │
│ adversarial auditing against marginalized sub-demographics.                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. WHAT HAPPENS WHEN THE AI IS WRONG?                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: The human operator overrides it instantly with a single click.│
│ The system captures the override, logs the reason, and preserves both the   │
│ AI output and human correction for continuous retraining and audit.         │
│ Technical Evidence: docs/product/HUMAN_OVERSIGHT.md (8 Override Actions);   │
│ packages/contracts/src/index.ts (OperatorOverrideActionSchema).             │
│ Demo Surface: Operator Workspace "Override Assessment" modal with reason.   │
│ Current Truth Status: CONTRACT_SPECIFIED.                                   │
│ Limitation: Requires trained operators who understand they have full       │
│ legal permission to overrule the algorithm.                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. CAN THE SYSTEM CALL THE POLICE OR DISPATCH AMBULANCES AUTOMATICALLY?     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: ABSOLUTELY NOT. Autonomous emergency dispatch is forbidden by │
│ system architecture. High-risk signals surface an alert to a human operator,│
│ and any multi-agency handoff requires authenticated supervisor approval.   │
│ Technical Evidence: docs/product/HUMAN_OVERSIGHT.md (Consequential Matrix); │
│ docs/product/IMMEDIATE_SAFETY_POLICY.md.                                    │
│ Demo Surface: Supervisor Emergency Action Approval Screen.                  │
│ Current Truth Status: ARCHITECTURALLY_ENFORCED.                             │
│ Limitation: Adds human verification latency (< 60s) to prevent catastrophic │
│ false-alarm armed raids on innocent households.                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 8. HOW DO YOU PREVENT BIAS AGAINST SPECIFIC CASTES, ACCENTS, OR GENDERS?    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: 1) Prohibit caste inference and voice profiling; 2) Separate  │
│ factual urgency from emotional presentation; 3) Enforce explicit uncertainty│
│ abstention when audio/dialect is ambiguous; 4) Continuous disaggregated WER.│
│ Technical Evidence: docs/product/RESOURCE_ROUTING_POLICY.md;                │
│ docs/product/LANGUAGE_POLICY.md; docs/traceability/CAPABILITY_STATUS.md.    │
│ Demo Surface: Golden Scenario F (Hinglish/Code-Switching preservation).     │
│ Current Truth Status: SPECIFIED_AND_GATED.                                  │
│ Limitation: Speech models in under-resourced tribal languages have higher   │
│ WER, requiring mandatory human operator language matching.                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 9. WHERE DOES YOUR TRAINING DATA COME FROM?                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: No live citizen grievance data is used without unbundled,     │
│ explicit consent. Foundational models utilize open government corpora       │
│ (Bhashini, AI4Bharat) and synthetic scenario corpora crafted under legal    │
│ and psychological supervision.                                              │
│ Technical Evidence: docs/privacy/CONSENT_MODEL.md;                          │
│ docs/ai/GOLDEN_SAFETY_CORPUS.md.                                            │
│ Demo Surface: Privacy Consent Banner showing separate research toggle.      │
│ Current Truth Status: CONSENT_LOCKED.                                       │
│ Limitation: Synthetic training data must be continually validated against   │
│ anonymized statutory court filings.                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 10. WHAT IF SOMEONE SOUNDS CALM WHILE FACING IMMINENT DANGER?               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: Guardrail 1 guarantees that explicit danger facts override    │
│ acoustic calm. A monotonic caller reporting an armed mob is classified as   │
│ CRITICAL Incident Urgency and CRITICAL_REVIEW Immediate Safety.             │
│ Technical Evidence: docs/product/ASSESSMENT_MODEL.md (Guardrail 1);         │
│ Golden Scenario A in docs/product/GOLDEN_SCENARIOS.md.                      │
│ Demo Surface: Live execution of Golden Scenario A test.                     │
│ Current Truth Status: VERIFIED_IN_SPEC.                                     │
│ Limitation: Relies on semantic detection of danger vocabulary or citizen    │
│ tap-based inputs.                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 11. WHAT IF ASR GETS A CRUCIAL PHRASE WRONG?                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: When ASR confidence drops, the system sets UncertaintyState to│
│ TRANSCRIPT_UNCERTAIN and suppresses autonomous categorization. The operator │
│ is alerted with audio playback to perform real-time text correction.        │
│ Technical Evidence: packages/contracts/src/index.ts (UncertaintyStateSchema);│
│ Golden Scenario G in docs/product/GOLDEN_SCENARIOS.md.                      │
│ Demo Surface: Operator Workspace inline ASR correction editor.              │
│ Current Truth Status: CONTRACT_SPECIFIED.                                   │
│ Limitation: Severe telephone packet drop requires operator verbal check.    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 12. WHAT IF THE CALLER SUDDENLY CHANGES LANGUAGES MID-SENTENCE?             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: SAMBAL is engineered for Indic code-switching (Hinglish/      │
│ Maranglish). The linguistic parser extracts semantic facts across mixed     │
│ vocabularies and tags vernacular idioms with their original audio tokens.   │
│ Technical Evidence: docs/product/LANGUAGE_POLICY.md; Golden Scenario F.     │
│ Demo Surface: Golden Scenario F test run.                                   │
│ Current Truth Status: BENCHMARK_SCHEDULED_P08.                              │
│ Limitation: Extreme multi-dialect switching flags LANGUAGE_UNCERTAIN for    │
│ human operator verification.                                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 13. HOW DOES THIS INTEGRATE WITH THE EXISTING NHAA (14566) SYSTEM?          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: SAMBAL acts as an intelligence-and-response layer augmenting  │
│ NHAA, not a disconnected silo. It ingests the live audio/web stream, runs   │
│ 3D triage, and outputs standardized case dossiers to the NHAA database.    │
│ Technical Evidence: docs/research/SAMBAL_NHAA_CURRENT_STATE.md;             │
│ docs/product/SERVICE_TAXONOMY.md.                                           │
│ Demo Surface: Canonical NHAA Adapter payload preview.                       │
│ Current Truth Status: ADAPTER_READY (Packet 19 formalization).              │
│ Limitation: Live government API integration requires formal MoSJE staging   │
│ credentials; verified locally in sandbox mode.                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 14. HOW DOES TELE-MANAS INTEGRATION ACTUALLY WORK?                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: Tele-MANAS (14416) provides 24/7 mental health care across 53 │
│ cells. SAMBAL prepares a consented, minimized psychosocial handoff packet   │
│ and establishes a warm voice transfer or digital referral into their queue. │
│ Technical Evidence: docs/product/SERVICE_TAXONOMY.md;                       │
│ docs/product/SAFE_HANDOFF.md.                                               │
│ Demo Surface: Tele-MANAS Consented Referral Packet Dispatch Screen.         │
│ Current Truth Status: ADAPTER_READY (Public baseline verified).             │
│ Limitation: Direct API trunk requires NIC/MoHFW peering; demonstrated via   │
│ compliant webhook sandbox.                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 15. HOW IS FREE LEGAL AID ACTUALLY CONNECTED?                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: Under Section 12(b) of the Legal Services Authorities Act,    │
│ all SC/ST persons are entitled to free legal aid. SAMBAL routes consented   │
│ fact dossiers directly to NALSA (15100), SLSA, or the local DLSA panel.     │
│ Technical Evidence: docs/product/SERVICE_TAXONOMY.md;                       │
│ packages/contracts/src/index.ts (SupportServiceTypeSchema).                 │
│ Demo Surface: DLSA Legal Referral Docket Generation.                        │
│ Current Truth Status: STATUTORY_BASELINE_VERIFIED.                          │
│ Limitation: Court appearance scheduling depends on DLSA panel advocate      │
│ roster capacity.                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 16. HOW DO YOU KNOW SUPPORT ACTUALLY REACHED THE VICTIM?                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: Through our 15-state Referral State Machine and 7-tier        │
│ Verified Support Hierarchy. A case is never closed on recommendation; it    │
│ requires dual-confirmation from both provider and citizen during follow-up. │
│ Technical Evidence: docs/product/REFERRAL_STATE_MACHINE.md;                 │
│ packages/contracts/src/index.ts (VerifiedSupportOutcomeSchema).             │
│ Demo Surface: Referral Tracking Lifecycle Visualizer.                       │
│ Current Truth Status: ARCHITECTURALLY_ENFORCED.                             │
│ Limitation: Requires citizen to respond to scheduled follow-up checks.      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 17. WHAT HAPPENS IF THERE IS NO SERVICE AVAILABLE IN A REMOTE DISTRICT?     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: The system never hides deficits. It vertically escalates the  │
│ case to the State Social Justice Nodal Desk, bridges to national telephony  │
│ trunks, and permanently records the shortage in Resource Gap Analytics.    │
│ Technical Evidence: docs/product/RESOURCE_ROUTING_POLICY.md (Section 4).    │
│ Demo Surface: Resource Gap Analytics Dashboard (Packet 22 Preview).         │
│ Current Truth Status: POLICY_SPECIFIED.                                     │
│ Limitation: Cannot physically manufacture doctors where none exist; alerts  │
│ administrators to budget and personnel deficits.                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 18. WHAT HAPPENS IF THE INTERNET OR CLOUD AI FAILS ENTIRELY?                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: The platform operates under Offline / Degraded Mode. Core     │
│ intake, deterministic regex safety filters, local SQLite/PostgreSQL caching,│
│ and telephony routing continue running without external cloud dependencies. │
│ Technical Evidence: Golden Scenario H; docs/results/01R-result.md (Docker). │
│ Demo Surface: Simulating network disconnect during active intake.           │
│ Current Truth Status: CORE_OFFLINE_CAPABLE.                                 │
│ Limitation: Advanced LLM summaries are disabled; fallback to rule templates.│
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 19. HOW IS CITIZEN PRIVACY PROTECTED UNDER THE DPDP ACT 2023?               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Short Answer: 1) Purpose-specific, unbundled consent; 2) Ephemeral audio    │
│ processing with zero default raw audio disk retention; 3) Role-based data   │
│ minimization per referral; 4) End-to-end PII masking in logs and telemetry. │
│ Technical Evidence: docs/privacy/CONSENT_MODEL.md;                          │
│ docs/privacy/DATA_MINIMIZATION.md; backend/app/logging.py.                  │
│ Demo Surface: Live Log Stream showing zero-leakage PII redaction.           │
│ Current Truth Status: HARDENED_IN_PKT_01R_AND_02.                           │
│ Limitation: Requires strict administrative compliance by operator staff.   │
└─────────────────────────────────────────────────────────────────────────────┘
```
