# SIH26093 — Problem Statement Deep Requirement Analysis

> **Document ID:** SIH26093-REQ-ANALYSIS-V2  
> **Problem Statement ID:** SIH26093  
> **Title:** AI-Based Real-Time Stress and Trauma Assessment Module for Victims/Complainants Accessing NHAA (14566) and Integrated Portal  
> **Sponsoring Body:** Ministry of Social Justice and Empowerment (MoSJE), Department of Social Justice and Empowerment (DoSJE)  
> **Theme:** MedTech / BioTech / HealthTech  
> **Category:** Software / Mission-Critical Public Sector AI  
> **Target Framework:** SAMBAL (Strengthening Access to Grievance Redressal) / NHAA Ecosystem

---

## 1. Statutory Context & Legal Ecosystem

The system operates in the statutory context of two foundational civil rights and anti-atrocity legislations in India:
1. **The Protection of Civil Rights Act, 1955 (PCR Act 1955):** Enacted to prescribe punishment for the preaching and practice of "Untouchability" and for the enforcement of any disability arising therefrom.
2. **The Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989 (PoA Act 1989, as amended in 2015 & 2018):** Enacted to prevent the commission of offences of atrocities against the members of SCs and STs, to provide for Special Courts and Exclusive Special Courts for the trial of such offences, and for the relief and rehabilitation of the victims of such offences.
3. **The Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Rules, 1995 (amended 2016):**
   - Mandates immediate relief and economic compensation to victims within statutory timeframes.
   - Mandates police investigation completion by a DSP-rank officer within 60 days.
   - Requires state witness and victim protection schemes.
   - Requires provision of legal aid, medical examination, socio-economic rehabilitation, and shelter.

### Why Standard Grievance Systems Fail for PoA Victims
Traditional grievance portals (e.g., generic municipal grievance trackers, basic CPGRAMS ticket forms) assume an administrative service deficit (e.g., a pothole, a delayed subsidy). In contrast, a complainant reaching out under the PoA Act via **14566** is frequently experiencing:
- **Severe Acute or Chronic Trauma:** Physical assault, caste-based humiliation, arson, sexual violence, or loss of family members.
- **Active Intimidation & Coercion:** Local dominant perpetrators threatening the victim or their family to withdraw police complaints (FIRs).
- **Social Boycott & Structural Isolation:** Cut off from village wells, shops, agricultural labor, or schooling.
- **Profound Power Asymmetry:** Facing hostile local power dynamics, fear of police retaliation, and procedural hurdles.
- **Fear of Reprisal:** Complainants may be in immediate physical danger while calling or using the portal.

---

## 2. Problem Statement Functional Breakdown

The official problem statement mandates a comprehensive, real-time intelligence module capable of transforming first-contact interactions into timely, verified, trauma-informed interventions.

### Dimension 1: Multimodal Ingestion (Voice & Text)
- **Voice Ingestion:** Must handle 24/7 telephone audio (narrowband 8kHz PSTN/VoIP) as well as portal/browser voice messages (16kHz+ web audio).
- **Text Ingestion:** Must process typed statements from web portals, chatbot transcripts, mobile app narratives, and operator-entered call summaries.
- **Silent Intake:** Must provide a dedicated channel for victims who cannot speak aloud due to the physical proximity of perpetrators.

### Dimension 2: Speech & Acoustic Feature Analytics
The system must extract objective acoustic and prosodic indicators without turning acoustic classifiers into pseudo-scientific psychiatric diagnoses:
- **Speech Rate & Fluency:** Syllables per second, sudden deceleration, or pressured speech.
- **Pause Architecture:** Duration, frequency, hesitation ratios, and silence bursts reflecting acute hesitation, suppression, or emotional flooding.
- **Pitch (F0) Dynamics:** Mean fundamental frequency, jitter, pitch variability, and micro-tremors indicating acute physiological arousal or distress.
- **Energy & Intensity:** Root Mean Square (RMS) energy shifts, shimmer, and voice drop-offs.
- **Audio Quality Index:** Signal-to-Noise Ratio (SNR), clipping, telephone band limitations, and background acoustic interference.

### Dimension 3: Multilingual NLP & Contextual Understanding
The linguistic diversity of complainants contacting 14566 across Indian states requires resilient multilingual NLP:
- **High-Coverage Languages:** Hindi, English, Marathi, Bengali, Tamil, Telugu, Kannada, Gujarati, Punjabi, Odia.
- **Code-Switching (Hinglish, Marathlish, Tanglish):** Frequent mixing of regional languages with English terms.
- **Complex Syntactic Structures:** Negation resolution, quoted speech, reported threats ("He said he will burn our house" vs "I want to burn our house"), and temporal referencing.
- **Trauma-Informed Semantic Categories:** Fear expressions, chronic helplessness, physical injuries, economic boycott, displacement, and threats to children.

### Dimension 4: Ethical Affective AI & Distress Signals
- Must recognize affective cues associated with acute distress, fear, anxiety, and grief.
- **Strict Boundary:** Affective features must serve as supporting evidence, never as standalone truth or diagnostic arbiters.
- Calm speech describing an armed mob must trigger **CRITICAL URGENCY**, completely overriding low acoustic arousal.

### Dimension 5: Suicidal Ideation & Imminent Self-Harm Engine
- Safety-critical detection operating via deterministic multilingual rule dictionaries, semantic sentence embeddings, and contextual reasoning.
- Must distinguish past historical distress from acute imminent intent.
- Must prevent catastrophic false negatives while guarding against keyword-overtriggering on colloquial metaphors.

### Dimension 6: Stress Vulnerability Index (SVI: 0–100)
- An explainable, policy-versioned composite index reflecting the complainant's overall vulnerability and need for comprehensive multi-agency intervention.
- Four explicit risk bands: **LOW (0–29)**, **MODERATE (30–59)**, **HIGH (60–84)**, and **CRITICAL (85–100)**.
- Every SVI computation must output the exact additive and multiplicative contributions of each evidence item.

### Dimension 7: Three-Dimensional Triage Model (USP 1)
Rather than collapsing all signals into a single score, the system must independently maintain:
1. **Immediate Safety Gate:** Evaluates active physical threat, active violence, or imminent self-harm.
2. **Stress Vulnerability Index (SVI):** Evaluates psychological, contextual, and structural vulnerability.
3. **Reported Incident Urgency:** Evaluates reported facts potentially relevant to urgency, statutory protection categories, and time-sensitive legal deadlines regardless of caller emotional expression. The system does NOT determine whether a crime legally occurred or whether an accused is guilty; legal characterization remains an authorized human/government responsibility.

### Dimension 8: Evidence Transparency & Counterfactual Reasoning (USP 2)
- Operators, supervisors, and judges must be able to inspect every piece of evidence (timestamp, modality, model version, confidence, SVI contribution).
- Counterfactual engine allows auditors to ask: *"What would the SVI be if acoustic features were excluded?"* or *"What if the reported threat was historical?"*

### Dimension 9: Closed-Loop Support Orchestration (USP 3)
The system does not terminate at a triage recommendation. It drives and tracks:
- **Counselling:** Referrals to Tele-MANAS (14416) or district psychological counsellors.
- **Legal Aid:** Direct handoff to National/District Legal Services Authorities (NALSA / DLSA).
- **Medical Assistance:** Hospital and medical examination coordination.
- **Police & Witness Protection:** Coordination with Special Atrocity Cells and District Magistrates.
- **Emergency Support & Shelter:** One-Stop Centres (OSC / Sakhi) and immediate relief funding.
- **Lifecycle Tracking:** Acknowledgement, appointment scheduling, support initiation, follow-up, and verified outcome logging.

---

## 3. Explicit Requirements Traceability Check

| SIH26093 Core Requirement | System Architectural Component | Verification Surface |
| :--- | :--- | :--- |
| Real-Time Speech Analytics | `SpeechAnalyticsEngine` (openSMILE / librosa / webrtcvad) | Operator Live Copilot & Evidence Timeline |
| Textual Narrative & Threat NLP | `TextSafetyEngine` & `MultilingualContextExtractor` | Live Transcript & Evidence Inspector |
| Emotion / Distress Detection | `AffectiveSignalEngine` (Bounded Acoustic Model) | Operator Co-pilot Supporting Signals |
| Suicidal Ideation Safety Gate | `SelfHarmSafetyEngine` (Deterministic Rules + Semantic) | High-Priority Operator Modal & Immediate Alert |
| Stress Vulnerability Index (SVI) | `MultimodalFusionEngine` (0–100, Configurable Policy) | SVI Dial, Evidence Breakdown, Counterfactuals |
| 4 Standard Risk Bands | `RiskBandClassifier` (LOW, MODERATE, HIGH, CRITICAL) | Triage Queue, Case Badges |
| Support Recommendations | `SupportRecommendationEngine` (Taxonomy-driven) | Action Card in Operator & Counsellor Hub |
| Multilingual & Dialect Resilience | `SpeechToTextProvider` & `TranslationProvider` | Language Selector, Code-Switch Benchmarks |
| Privacy & Ethical Safeguards | `PrivacyEngine`, `ConsentManager`, `AuditLogger` | Citizen Privacy Center, Audit Trails |
| Closed-Loop Outcome Tracking | `ReferralLifecycleEngine` & `FollowupCoordinator` | Closed-Loop Case Journey & Outcomes Dashboard |

---

## 4. Operational Context & Capabilities Documented in Public Sources

Public official materials reviewed document grievance registration, docket tracking, escalation/reminder and citizen feedback capabilities within the NHAA (14566) and SAMBAL portals. However, published materials do not document the real-time multimodal vulnerability assessment, trauma-aware co-pilot guidance, and closed-loop cross-service support orchestration required by SIH26093:
1. **Intake Capabilities:** Public portals provide structured grievance logging and docket generation, but lack real-time acoustic/prosodic or semantic distress analysis during active calls.
2. **Dissociated / Calm Complainant Handling:** Guidance tools are needed to prevent cases where calm callers reporting extreme ongoing violence are inadvertently assigned low priority.
3. **Cross-Agency Handoff Telemetry:** While administrative dockets are redirected to District Magistrates or Police Superintendents, automated closed-loop integration with mental health (Tele-MANAS 14416) or legal aid (NALSA) is not documented.
4. **SAMBAL Intelligence Layer Role:** Acts as an augmentative intelligence and response layer running alongside NHAA and portal sessions, surfacing immediate threats, guiding the operator with trauma-informed prompts, and orchestrating closed-loop service delivery.
