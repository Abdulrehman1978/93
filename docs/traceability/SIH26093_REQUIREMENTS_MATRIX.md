# SIH26093 — Master Atomic Requirements Traceability Matrix

> **Document ID:** SIH26093-TRACEABILITY-MATRIX-V2  
> **Standard:** Mandatory 100% Granular Traceability from Problem Statement to Code, API, UI, Tests, and Demo Scenarios.  
> **Status Conventions:** `NOT_STARTED` | `IN_PROGRESS` | `PASS` | `PASS_WITH_EXTERNAL_DEPENDENCY` | `BLOCKED`

---

## 1. Atomic Requirements Matrix

| Atomic Req ID | Parent | SIH26093 Interpreted Capability | Product Feature / Contract | Backend Domain Module | Frontend Surface | Verification Test ID | Demo Scenario | Status | Documented Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `REQ-01.1` | `REQ-01` | Syllable speech tempo & speaking rate calculation | `SpeechTempoExtractor` | `app.intelligence.speech` | Waveform HUD (`/operator/live`) | `test_speech_rate_extraction` | Scenario A | `IN_PROGRESS` | Rapid speakers without distress may require baseline calibration. |
| `REQ-01.2` | `REQ-01` | Pause duration, frequency & hesitation ratio | `PauseArchitectureAnalyzer` | `app.intelligence.speech` | Timeline Markers (`/operator/live`) | `test_pause_hesitation_ratio` | Scenario A, G | `IN_PROGRESS` | Caller pauses due to poor cellular reception must be differentiated. |
| `REQ-01.3` | `REQ-01` | Pitch (F0) tracking & micro-tremor analysis | `PitchDynamicsAnalyzer` | `app.intelligence.speech` | Acoustic Inspector Drawer | `test_pitch_f0_pyin_tracking` | Scenario G | `IN_PROGRESS` | 8kHz telephone audio roll-off limits high-formant harmonics. |
| `REQ-01.4` | `REQ-01` | RMS energy shifts & vocal drop-off detection | `IntensityShimmerAnalyzer` | `app.intelligence.speech` | Waveform HUD (`/operator/live`) | `test_rms_intensity_shifts` | Scenario G | `IN_PROGRESS` | Speakerphone volume changes can induce artificial energy drops. |
| `REQ-01.5` | `REQ-01` | Audio Quality Index (AQI) & SNR calculation | `AudioQualityEvaluator` | `app.intelligence.speech` | Audio Quality Badge (`/operator/live`) | `test_snr_audio_quality_flag` | Scenario G | `IN_PROGRESS` | Low SNR triggers acoustic abstention. |
| `REQ-02.1` | `REQ-02` | Structured text narrative intake with guided prompts | `TypedNarrativeIntake` | `app.channel.text` | Text Intake (`/intake/text`) | `test_typed_narrative_intake` | Citizen Flow | `IN_PROGRESS` | Users with low literacy require voice or tap-based options. |
| `REQ-02.2` | `REQ-02` | Streaming transcript normalization & script preservation | `TranscriptNormalizer` | `app.speech.indic` | Live Transcript Pane | `test_transcript_script_preservation` | Scenario F | `IN_PROGRESS` | Dialectal phonetic variations preserved in native script. |
| `REQ-02.3` | `REQ-02` | Operator-entered call summary with explicit provenance | `OperatorSummaryIngest` | `app.case.intake` | Case Summary Editor | `test_operator_summary_provenance` | Operator Hub | `IN_PROGRESS` | Operator notes must never overwrite complainant testimony. |
| `REQ-03.1` | `REQ-03` | Bounded affective distress classification (fear, distress, flat) | `AffectiveDistressClassifier` | `app.intelligence.affective` | Supporting Signal Badges | `test_affective_signal_bounds` | Scenario A, G | `IN_PROGRESS` | Bounded to max ±15 pts SVI; research-informed signal only. |
| `REQ-03.2` | `REQ-03` | Acoustic veto boundary (calm voice does not down-rank threat) | `AcousticVetoGuardrail` | `app.intelligence.fusion` | Urgency Warning Banner | `test_calm_voice_veto_rule` | Scenario A | `IN_PROGRESS` | Textual threat strictly overrules low acoustic distress. |
| `REQ-03.3` | `REQ-03` | Acoustic abstention on low audio quality (SNR < 10dB) | `AcousticAbstentionHandler` | `app.intelligence.affective` | Quality Warning Alert | `test_acoustic_quality_abstention` | Scenario G | `IN_PROGRESS` | Acoustic weight clamps to 0; confidence interval widens. |
| `REQ-04.1` | `REQ-04` | Deterministic multilingual present-tense self-harm detection | `DeterministicSelfHarmRules` | `app.safety.self_harm` | Red Safety Modal (`/operator/live`) | `test_golden_self_harm_recall` | Scenario B | `IN_PROGRESS` | Safety-critical; must achieve 100% recall on golden phrases. |
| `REQ-04.2` | `REQ-04` | Semantic negation disambiguation for self-harm phrases | `SelfHarmNegationResolver` | `app.safety.self_harm` | Safety Status Indicator | `test_self_harm_negation_resolver` | Scenario C | `IN_PROGRESS` | "Not thinking of suicide" must avoid emergency alarm. |
| `REQ-04.3` | `REQ-04` | Historical vs. acute self-harm temporal classification | `TemporalHarmDisambiguator` | `app.safety.self_harm` | Vulnerability Context Tag | `test_historical_self_harm_tagging` | Golden Corpus | `IN_PROGRESS` | Past historical trauma flags vulnerability, not immediate alert. |
| `REQ-05.1` | `REQ-05` | Direct violence & weapon threat extraction | `ViolenceThreatExtractor` | `app.intelligence.threat` | Threat Callout Card | `test_weapon_violence_extraction` | Scenario A, D | `IN_PROGRESS` | Requires entity matching across regional weapon terms. |
| `REQ-05.2` | `REQ-05` | Coercion & forced complaint withdrawal detection | `CoercionRetaliationEngine` | `app.intelligence.threat` | Intimidation Pin on Timeline | `test_coercion_withdrawal_detection` | Scenario D | `IN_PROGRESS` | Pressure from village panchayats or police intermediaries. |
| `REQ-05.3` | `REQ-05` | Social boycott, water access denial & economic isolation | `StructuralVulnerabilityModel` | `app.intelligence.context` | Structural Vulnerability Badge | `test_social_boycott_detection` | 3-Min Demo | `IN_PROGRESS` | PoA Act Section 3(1)(za) socio-economic boycott patterns. |
| `REQ-06.1` | `REQ-06` | SVI qualitative triage band assessment & multimodal fusion | `SVICompositeScorer` | `app.intelligence.svi` | SVI Dial (`/operator/live`) | `test_svi_mathematical_bounds` | Scenario A, F | `IN_PROGRESS` | Conceptually 0–100; mathematical fusion evaluated in P11. |
| `REQ-06.2` | `REQ-06` | Provisional triage policy versioning (`SVI_POLICY_STATUS`) | `SVIPolicyRegistry` | `app.intelligence.policy` | Policy Version Tag | `test_svi_policy_version_stamp` | Technical Demo | `IN_PROGRESS` | Labelled `PROVISIONAL_TRIAGE_POLICY` pending clinical study. |
| `REQ-06.3` | `REQ-06` | Evidence attribution tracking without premature additive weights | `SVIEvidenceAttributionEngine` | `app.intelligence.svi` | Evidence Inspector Drawer | `test_svi_attribution_breakdown` | 3-Min Demo | `IN_PROGRESS` | References source pointers; zero static linear weights. |
| `REQ-07.1` | `REQ-07` | Deterministic 4-band partition (Low, Mod, High, Critical) | `RiskBandClassifier` | `app.intelligence.bands` | Risk Band Badge (`/operator/queue`) | `test_risk_band_partitions` | Scenario A, B, E | `IN_PROGRESS` | Conceptual triage bands for prioritized operator review. |
| `REQ-07.2` | `REQ-07` | Explainable priority queue sorting (Urgency + SVI + Age) | `PriorityQueueManager` | `app.case.queue` | Operator Triage Queue | `test_queue_sorting_composite` | Operator Hub | `IN_PROGRESS` | Prioritizes active physical danger over acoustic distress alone. |
| `REQ-08.1` | `REQ-08` | Immediate Safety Gate evaluation (independent of SVI) | `ImmediateSafetyGate` | `app.safety.immediate` | Persistent Red Safety Banner | `test_immediate_safety_gate` | Scenario A, B | `IN_PROGRESS` | Evaluates active physical threat or suicide intent. |
| `REQ-08.2` | `REQ-08` | Fast-path operator alert modal with safety question prompts | `SafetyAlertModal` | `app.copilot.alerts` | Safety Action Modal | `test_safety_alert_modal_trigger` | Scenario B | `IN_PROGRESS` | High-priority WebSocket push to active operator console. |
| `REQ-09.1` | `REQ-09` | Reported Incident Urgency scoring (PoA fact identification) | `ReportedIncidentUrgencyModel` | `app.intelligence.urgency` | Reported Urgency Indicator | `test_reported_urgency_scoring` | Scenario A | `IN_PROGRESS` | Evaluates reported facts relevant to statutory protection. |
| `REQ-09.2` | `REQ-09` | Legal non-adjudication boundary (AI does not determine guilt) | `LegalBoundaryGuardrail` | `app.intelligence.urgency` | Ethical Notice Disclaimer | `test_legal_boundary_disclaimer` | Admin View | `IN_PROGRESS` | Legal characterization strictly reserved for human authorities. |
| `REQ-10.1` | `REQ-10` | Tele-MANAS (14416) mental health counseling recommendation | `TeleManasRecommender` | `app.orchestration.recommend` | Action Card: Counseling | `test_telemanas_recommendation` | 3-Min Demo | `IN_PROGRESS` | Recommends counseling based on distress indicators. |
| `REQ-10.2` | `REQ-10` | DLSA free legal aid & Section 15A protection recommendation | `LegalAidRecommender` | `app.orchestration.recommend` | Action Card: Legal Aid | `test_legal_aid_recommendation` | 3-Min Demo | `IN_PROGRESS` | Triggers statutory right to free lawyer under LSA Act Sec 12. |
| `REQ-10.3` | `REQ-10` | Emergency medical examination & hospital assistance matching | `MedicalAidRecommender` | `app.orchestration.recommend` | Action Card: Medical | `test_medical_aid_recommendation` | Case Actions | `IN_PROGRESS` | Matched when physical assault or injury is reported. |
| `REQ-10.4` | `REQ-10` | One-Stop Sakhi Centre shelter & PoA relief recommendation | `ShelterReliefRecommender` | `app.orchestration.recommend` | Action Card: Shelter/Relief | `test_shelter_relief_recommend` | Case Actions | `IN_PROGRESS` | Recommends emergency shelter and statutory compensation. |
| `REQ-11.1` | `REQ-11` | Indic Multilingual ASR (Baseline Candidate: faster-whisper-turbo) | `ASRProvider (CTranslate2)` | `app.speech.transcription` | Live Transcript (`/operator/live`) | `test_asr_indic_transcription` | Scenario F | `IN_PROGRESS` | Initial baseline; final selection subject to Packet 08 benchmarks. |
| `REQ-11.2` | `REQ-11` | Colloquial code-switching ingestion (Hinglish, Marathlish) | `CodeSwitchingProcessor` | `app.speech.indic` | Live Transcript Pane | `test_code_switching_accuracy` | Scenario F | `IN_PROGRESS` | Preserves English technical/legal loanwords in regional text. |
| `REQ-11.3` | `REQ-11` | Dialect uncertainty propagation into SVI confidence intervals | `ASRUncertaintyPropagator` | `app.intelligence.fusion` | Confidence Interval Gauge | `test_uncertainty_propagation` | Scenario G | `IN_PROGRESS` | Low ASR confidence widens downstream SVI error bands. |
| `REQ-12.1` | `REQ-12` | Interactive synchronized timeline (Waveform + Transcript + Pins) | `EvidenceTimelineVisualizer` | `app.copilot.timeline` | Canvas Waveform & Timeline | `test_timeline_sync_events` | 3-Min Demo | `IN_PROGRESS` | Synchronizes audio playback with transcript and risk pins. |
| `REQ-12.2` | `REQ-12` | Deep Evidence Inspector (snippet, modality, model, SNR, score) | `EvidenceInspectorEngine` | `app.copilot.inspector` | Inspector Drawer (`/operator/live`) | `test_inspector_payload_schema` | 3-Min Demo | `IN_PROGRESS` | Full transparency into why every indicator was flagged. |
| `REQ-12.3` | `REQ-12` | Counterfactual SVI impact analysis (e.g. exclude acoustic signal) | `CounterfactualEvaluator` | `app.intelligence.svi` | Counterfactual Sliders | `test_counterfactual_delta_calc` | Technical Demo | `IN_PROGRESS` | Enables auditors to test score sensitivity to single factors. |
| `REQ-13.1` | `REQ-13` | Closed-loop referral state machine (15 auditable states) | `ReferralLifecycleEngine` | `app.referral.lifecycle` | Referral Journey Tracker | `test_referral_state_transitions` | 3-Min Demo | `IN_PROGRESS` | Enforces state progression from RECOMMENDED to OUTCOME. |
| `REQ-13.2` | `REQ-13` | SLA breach timers & automated supervisor escalation | `ReferralSLAMonitor` | `app.referral.sla` | Supervisor Alert Banner | `test_sla_breach_escalation` | Supervisor Hub | `IN_PROGRESS` | Alerts if critical referral unacknowledged within SLA. |
| `REQ-13.3` | `REQ-13` | Policy-driven follow-up scheduling (`FollowUpPolicy` model) | `FollowUpScheduler` | `app.referral.followup` | Follow-up Queue (`/support/followups`) | `test_policy_driven_followup` | Case Tracker | `IN_PROGRESS` | Configurable intervals based on risk band and service type. |
| `REQ-14.1` | `REQ-14` | Granular DPDP-ready consent center & processing-purpose scoping | `DPDPConsentManager` | `app.privacy.consent` | Consent Center (`/privacy-controls`) | `test_dpdp_granular_consent` | Citizen Flow | `IN_PROGRESS` | Separates transcription, assessment, referral, and research. |
| `REQ-14.2` | `REQ-14` | Ephemeral audio disposal & zero voiceprint profiling policy | `EphemeralAudioPurgeEngine` | `app.privacy.retention` | Privacy Verification Tag | `test_ephemeral_audio_purge` | Security Audit | `IN_PROGRESS` | In-memory raw audio discarded after session extraction. |
| `REQ-15.1` | `REQ-15` | Silent distress intake flow (tap-based, zero vocalization) | `SilentDistressWorkflow` | `app.channel.silent` | Silent Intake (`/intake/silent`) | `test_silent_flow_execution` | Scenario E | `IN_PROGRESS` | Designed for victims trapped with perpetrators. |
| `REQ-15.2` | `REQ-15` | Emergency Quick Exit button & local cache cleansing | `QuickExitSecurityController` | `app.channel.silent` | Quick Exit Control (Persistent) | `test_quick_exit_redirect` | Scenario E | `IN_PROGRESS` | Instant redirect to neutral portal; purges client sessionStorage. |
| `REQ-16.1` | `REQ-16` | "Share Less" consented redacted Safe Handoff Package | `SafeHandoffPackager` | `app.referral.handoff` | Handoff Review Modal | `test_safe_handoff_redaction` | Counsellor Flow | `IN_PROGRESS` | Minimizes victim PII; excludes raw audio and SVI scores. |
| `REQ-16.2` | `REQ-16` | Never-Repeat-My-Story fact provenance memory layer | `CaseMemoryStore` | `app.case.memory` | Case Intelligence View | `test_never_repeat_provenance` | Case View | `IN_PROGRESS` | Distinctly tags Complainant, AI, Operator, and Provider facts. |
| `REQ-17.1` | `REQ-17` | Protocol-backed suggested next trauma questions | `PromptAdvisoryEngine` | `app.copilot.prompts` | Suggested Question Card | `test_protocol_question_selection` | 3-Min Demo | `IN_PROGRESS` | Suggests vetted trauma-informed questions for missing data. |
| `REQ-17.2` | `REQ-17` | Operator question dismissal & non-autonomous speech | `PromptGovernanceGuard` | `app.copilot.prompts` | Dismiss / Modify Buttons | `test_prompt_dismissal_tracking` | Operator Hub | `IN_PROGRESS` | AI never speaks automatically; operator retains full agency. |
| `REQ-18.1` | `REQ-18` | Privacy-preserving district resource gap intelligence | `ResourceGapAnalyticsEngine` | `app.analytics.gaps` | Resource Gap Map (`/admin/gaps`) | `test_resource_gap_aggregation` | Admin View | `IN_PROGRESS` | Aggregates district-level counseling deficits with $k \ge 10$. |
| `REQ-19.1` | `REQ-19` | Headless Modular Monolith REST & WebSocket API gateway | `HeadlessAPIGateway` | `app.api.v1` | OpenAPI 3.1 Docs (`/api/docs`) | `test_headless_openapi_spec` | Technical Demo | `IN_PROGRESS` | Reusable intelligence engine callable by any external client. |
| `REQ-19.2` | `REQ-19` | Canonical support adapters (TeleManas, NALSA, ERSS112 Sandbox) | `ExternalAdapterGateway` | `app.integrations` | Adapter Status Dashboard | `test_adapter_dispatch_sandbox` | Technical Demo | `IN_PROGRESS` | Sandbox mode simulates external callbacks and HMAC signatures. |
| `REQ-19.3` | `REQ-19` | Human-authorized emergency dispatch boundary (`ERSS112Adapter`) | `EmergencyAuthorizationGate` | `app.integrations.erss` | Emergency Dispatch Modal | `test_emergency_dispatch_human_gate` | Security Audit | `IN_PROGRESS` | Autonomous dispatch strictly barred; requires human operator click. |
| `REQ-20.1` | `REQ-20` | Circuit breaker & fallback to offline deterministic safety | `DegradedModeManager` | `app.core.resilience` | Degraded Status Banner | `test_offline_circuit_breaker` | Scenario H | `IN_PROGRESS` | System remains fully functional during external LLM cloud outage. |
| `REQ-20.2` | `REQ-20` | Canonical PostgreSQL database foundation (Budget: 32–40 tables) | `PostgreSQLDatabaseManager` | `app.db` | DB Health Telemetry (`/health/db`) | `test_canonical_postgres_connection` | CI / Foundation | `IN_PROGRESS` | PostgreSQL 16+ is canonical; strict upper budget $\le 45$ tables. |

## Packet 06 traceability addendum

| Requirement | Implemented boundary | Evidence | Status |
| --- | --- | --- | --- |
| Canonical channel gateway | `/api/v1/channel/*`, canonical registry, provider-neutral adapter contract | `backend/app/channel/`, `docs/channel/CHANNEL_GATEWAY.md` | Implemented; external adapters not configured |
| Anonymous session security | Digest-only session token, idle/absolute expiry, safe invalid-session response | `backend/app/channel/session.py`, `docs/channel/SESSION_POLICY.md` | Implemented |
| Purpose-limited consent | Notice-before-decision, stale policy, append-only revocation, action idempotency | `backend/app/privacy/consent_engine.py`, `docs/privacy/CONSENT_ENGINE.md` | Implemented |
| Pre-case interaction | Subject-bound interaction with nullable case and validated internal binding | migration `0009_channel_gateway_consent`, schema invariants | Implemented |

## Packet 07 traceability addendum

| Requirement | Implemented boundary | Evidence | Status |
| --- | --- | --- | --- |
| Citizen chooses Speak / Write / Silent | `/help`, `/help/speak`, `/help/write`, `/help/silent` with truthful mode registry | `apps/web/src/components/citizen/intake-flow.tsx`; Packet 07 Playwright | Implemented; Speak pre-capture only |
| Trauma-informed intake | Optional fields, no forced legal fields, one-question Silent flow, review/edit, recovery copy | `docs/product/CITIZEN_INTAKE.md`; `apps/web/src/app/globals.css` | Implemented |
| Quick Exit | Button + Escape, session/draft purge, neutral `location.replace`, no-referrer response headers | `docs/product/QUICK_EXIT.md`; `quick-exit.tsx` | Implemented |
| Atomic encrypted citizen submission | Encrypted append-only entry table, OPEN NORMAL case, case binding, authorization promotion, receipt idempotency | `backend/app/intake/service.py`; migration `0012`; Packet 07 integration tests | Implemented; PostgreSQL CI gate |
| No premature voice/AI capability | No microphone/Web Speech/getUserMedia/audio upload/NLP/AI path in Packet 07 | `docs/results/07-result.md`; Speak route test | Implemented truth boundary |

---

## 2. SIH26093 Problem Statement Itemized Coverage Gate (35 Mandatory Terms)

The table below provides granular proof that all 35 explicit terms from the SIH26093 problem statement have documented product behavior, governance policies, implementation assignments, and verification scenarios:

| # | Problem Statement Term | Product Concept | Policy Document Reference | Future Packet Assignment | Verification Test / Demo Scenario |
| :-: | :--- | :--- | :--- | :---: | :--- |
| **1** | **Voice Analysis** | Non-semantic acoustic feature extraction (F0, tremor, SNR) | `docs/ai/AFFECTIVE_SIGNAL_POLICY.md` | **Packet 10** | `tests/test_speech_analytics.py` (Scenario G) |
| **2** | **Pauses** | Speech-pause architecture & hesitation ratio analysis | `docs/ai/AFFECTIVE_SIGNAL_POLICY.md` | **Packet 10** | `test_pause_hesitation_ratio` (Scenario A) |
| **3** | **Pitch Variation** | Fundamental frequency (F0) perturbation & micro-tremor tracking | `docs/ai/AFFECTIVE_SIGNAL_POLICY.md` | **Packet 10** | `test_pitch_f0_pyin_tracking` (Scenario G) |
| **4** | **Speech Patterns** | Syllable tempo, speech rate, and vocal intensity drop-off | `docs/ai/AFFECTIVE_SIGNAL_POLICY.md` | **Packet 10** | `test_speech_rate_extraction` (Scenario A) |
| **5** | **Emotional Indicators** | Bounded prosodic distress cues (`SUPPORTING_SIGNAL_ONLY`) | `docs/ai/AFFECTIVE_SIGNAL_POLICY.md` | **Packet 10** | `test_affective_signal_bounds` (Scenario A) |
| **6** | **Text Narratives** | Multi-channel citizen typed / written narrative intake | `docs/product/JOURNEYS.md` (Journey 2) | **Packet 07** | `test_typed_narrative_intake` (Citizen Flow) |
| **7** | **NLP** | Multilingual entity extraction, negation, and temporal parsing | `docs/ai/GOLDEN_SAFETY_CORPUS.md` | **Packet 09** | `test_text_safety.py` (Scenario F) |
| **8** | **Speech Analytics** | DSP-based speech quality index and acoustic anomaly detection | `backend/app/intelligence/contracts.py` | **Packet 10** | `test_snr_audio_quality_flag` (Scenario G) |
| **9** | **Emotion AI** | Operator empathy pacing telemetry (strictly non-diagnostic) | `docs/ai/AFFECTIVE_SIGNAL_POLICY.md` | **Packet 10** | Operator Copilot Inspector (Scenario A) |
| **10**| **SVI (Stress Vulnerability Index)** | Multidimensional triage prioritization band (0–100 concept) | `docs/ai/SVI_POLICY.md` | **Packet 11** | `test_svi_mathematical_bounds` (Golden Lab) |
| **11**| **Low / Moderate / High / Critical** | 4 standardized operational triage bands for review ordering | `docs/ai/SVI_POLICY.md` | **Packet 11** | `test_risk_band_partitions` (Scenarios A, B, E) |
| **12**| **Severe Trauma Indicators** | Compound trauma recall, panic symptoms, and grief detection | `docs/product/ASSESSMENT_MODEL.md` | **Packet 09, 11**| `test_trauma_distress_extraction` (Golden B) |
| **13**| **Fear** | Acoustic tremor combined with explicit threat narrative | `docs/product/ASSESSMENT_MODEL.md` | **Packet 09, 10**| Scenario D (Witness Intimidation) |
| **14**| **Depression-Associated Indicators** | Passive hopelessness, existential despair, sleep/energy complaints | `docs/product/SELF_HARM_SAFETY_POLICY.md` | **Packet 09** | `test_passive_hopelessness` (Category 2) |
| **15**| **Suicidal Ideation** | 7-part context semantics taxonomy with zero-tolerance recall | `docs/product/SELF_HARM_SAFETY_POLICY.md` | **Packet 09** | `test_golden_self_harm_recall` (Scenario B, C) |
| **16**| **Intimidation** | Coercion, stalking, witness pressure, and threats of violence | `docs/product/REPORTED_INCIDENT_URGENCY.md`| **Packet 09** | Scenario D (Accused Death Threats) |
| **17**| **Social Isolation** | Community boycotts, water/electricity denial, movement barriers | `docs/product/REPORTED_INCIDENT_URGENCY.md`| **Packet 09** | Scenario A (Colony Siege) |
| **18**| **Extreme Vulnerability** | Compound physical, social, and psychological crisis (`CRITICAL`) | `docs/ai/SVI_POLICY.md` | **Packet 11** | Operator Queue Priority 1 (Scenario B) |
| **19**| **Counselling** | Frontline psychosocial support & supportive listening | `docs/product/SERVICE_TAXONOMY.md` | **Packet 14, 15**| Tele-MANAS Tier-1 Matching (Scenario B) |
| **20**| **Legal Aid** | Free legal representation under LSA Act 1987 Section 12(b) | `docs/product/SERVICE_TAXONOMY.md` | **Packet 14, 15**| NALSA 15100 Docket Dispatch (Scenario F) |
| **21**| **Medical Support** | Medico-legal examination & emergency hospital treatment | `docs/product/SERVICE_TAXONOMY.md` | **Packet 14, 15**| Civil Hospital Emergency Referral |
| **22**| **Police Intervention Review** | Authorized administrative review of protection & FIR registration| `docs/product/SERVICE_TAXONOMY.md` | **Packet 14, 15**| District SP / SC/ST Cell Notification |
| **23**| **Witness Protection Review** | Threat assessment dossier for District Witness Protection Committee | `docs/product/SERVICE_TAXONOMY.md` | **Packet 14, 15**| Witness Protection Dossier Generator |
| **24**| **Emergency Support** | Human-authorized emergency rescue coordination via ERSS 112 | `docs/product/SERVICE_TAXONOMY.md` | **Packet 14, 15**| ERSS 112 Multi-Agency Conference Call |
| **25**| **Indian Languages** | Explicit 7-dimension language registry (English, Hindi, Marathi) | `docs/product/LANGUAGE_POLICY.md` | **Packet 08** | Multilingual ASR Benchmark Suite |
| **26**| **Dialect / Code-Switch Uncertainty** | Hinglish/Maranglish token preservation & `LANGUAGE_UNCERTAIN` | `docs/product/LANGUAGE_POLICY.md` | **Packet 08, 09**| Golden Scenario F Test |
| **27**| **Privacy** | DPDP Act 2023 compliance, purpose limitation & data minimization | `docs/privacy/DATA_MINIMIZATION.md` | **Packet 04** | PII Redaction Audit in Logs & Telemetry |
| **28**| **Consent** | 7-part unbundled consent model; research consent fully optional | `docs/privacy/CONSENT_MODEL.md` | **Packet 06** | Consent Ledger Token Verification |
| **29**| **Confidentiality** | Role-scoped Safe Handoff packets; zero unconsented data dumps | `docs/product/SAFE_HANDOFF.md` | **Packet 16** | Inter-Agency Data Sieve Audit |
| **30**| **Ethical AI** | Prohibitions on guilt scoring, lie detection, and clinical diagnoses| `docs/product/ASSESSMENT_MODEL.md` | **Packet 26** | Algorithmic Fairness & Parity Audits |
| **31**| **Early Identification** | Sub-3-second visual triage for incoming helpline interactions | `docs/product/JOURNEYS.md` (Journey 5) | **Packet 13** | Operator Triage Latency Benchmark |
| **32**| **Prioritisation** | 3D queue sorting (Immediate Safety > Incident Urgency > SVI > Age) | `docs/product/ASSESSMENT_MODEL.md` | **Packet 13** | Priority Queue Sorting Unit Tests |
| **33**| **Victim-Centric Redressal** | Civic Calm UX, trauma-informed copy, and non-coercive choices | `docs/product/TRAUMA_INFORMED_UX.md` | **Packet 05, 07**| Complainant User Journey Evaluation |
| **34**| **Resource Allocation** | Objective matching criteria & district-level resource gap maps | `docs/product/RESOURCE_ROUTING_POLICY.md`| **Packet 14, 22**| District Resource Deficit Dashboard |
| **35**| **Responsiveness** | Automated SLA tracking, timeout escalations, and verified follow-up | `docs/product/REFERRAL_STATE_MACHINE.md`| **Packet 15** | Referral SLA Escalation Monitor Test |
