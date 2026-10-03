# Multimodal AI Pipeline & Evidence Fusion Architecture

> **Document ID:** ARCH-AI-PIPELINE-V2  
> **Topic:** Multi-Tier AI Architecture, Evidence Fusion, SVI Mathematical Formulation, and Counterfactual Reasoning  
> **Core Principle:** Evidence instead of mysterious AI — Bounded Models, Strict Ethical Limits, No Black Boxes.

---

## 1. Multimodal AI Pipeline Flow

```text
                           RAW COMPLAINT INPUT
                       (Voice Audio or Text Narrative)
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
[ AUDIO MODALITY PIPELINE ]                             [ TEXT MODALITY PIPELINE ]
├── WebRTC VAD Pause Tracker                            ├── Language & Code-Switch Detector
├── DSP Acoustic Feature Extractor (pyin, RMS, rate)    ├── Normalizer & Script Preserver
├── faster-whisper-turbo Multilingual ASR               ├── Layer 1: Deterministic Safety Rules
└── Affective Distress Classifier (Bounded ±15)         ├── Layer 2: Semantic Threat Classifier
         │                                              └── Layer 3: Contextual Extraction
         └───────────────────────────┬───────────────────────────┘
                                     │
                                     ▼
                      [ MULTIMODAL EVIDENCE FUSION ]
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
[ 1. IMMEDIATE SAFETY GATE ]  [ 2. STRESS VULNERABILITY ]  [ 3. INCIDENT URGENCY ]
├── Physical Assault Threat   ├── SVI Score: 0 – 100      ├── PoA Act Offence Tier
├── Active Weapons Nearby     ├── 4 Risk Bands:           ├── Retaliation History
├── Present Self-Harm Intent  │   • LOW (0–29)            ├── Vulnerable Dep. (Kids)
└── OVERRIDE: CRITICAL ALERT  │   • MODERATE (30–59)      └── Independent of voice
                              │   • HIGH (60–84)
                              │   • CRITICAL (85–100)
                              └── Contribution Attribution
                                     │
                                     ▼
                    [ SUPPORT RECOMMENDATION ENGINE ]
                    ├── Tele-MANAS Counseling
                    ├── DLSA Legal Aid (Section 15A)
                    ├── Police Atrocity Protection Cell
                    ├── Medical / Hospital Assistance
                    └── Emergency Shelter / One-Stop Sakhi
```

---

## 2. Stress Vulnerability Index (SVI) Mathematical Formulation

The **Stress Vulnerability Index (SVI)** is an interpretable, additive, policy-versioned composite score bounded on the interval $[0, 100]$.

$$\text{SVI} = \min\left(100, \max\left(0, \sum_{i=1}^{n} w_i \cdot E_i + \Delta_{\text{affective}} + \Delta_{\text{contextual}}\right)\right)$$

### Parameter Definitions & Weight Budget:

| Evidence Factor ($E_i$) | Modality | Detection Mechanism | Weight Range ($w_i$) | Default Contribution |
| :--- | :--- | :--- | :--- | :--- |
| **Explicit Danger to Life / Threats** | Text (Transcript/Typed) | Layer 1 Deterministic + Layer 2 Semantic | $0.25 - 0.35$ | $+25 \text{ to } +35 \text{ pts}$ |
| **Active Intimidation / Coercion** | Text (Transcript/Typed) | Layer 2 Semantic Threat Classifier | $0.15 - 0.25$ | $+18 \text{ to } +25 \text{ pts}$ |
| **Severe Distress Language** | Text (Transcript/Typed) | Multilingual Distress Lexicon & Embeddings | $0.10 - 0.20$ | $+12 \text{ to } +20 \text{ pts}$ |
| **Social Boycott / Displacement** | Text / Context | Structural Vulnerability Classifier | $0.10 - 0.15$ | $+10 \text{ to } +15 \text{ pts}$ |
| **Lack of Safe Social Support** | Contextual Self-Report | Intake Questionnaire Extraction | $0.05 - 0.10$ | $+8 \text{ to } +12 \text{ pts}$ |
| **Prolonged Hesitation / Pauses** | Speech (Acoustic DSP) | WebRTC VAD Pause Frequency & Hesitation Ratio | $0.05 - 0.10$ | $+5 \text{ to } +10 \text{ pts}$ |
| **Affective Distress Arousal** | Speech (Affective AI) | Bounded wav2vec2 Prosodic Signal Model | Bounded: $[-10, +15]$ | Max $+15 \text{ pts}$ |

### Strict Bounded Affective AI Guardrail:
- **Maximum Influence:** $\Delta_{\text{affective}} \in [-10, +15]$.
- **Veto Rule:** If explicit text indicators report an ongoing threat or assault, a low or calm acoustic signal ($\Delta_{\text{affective}} \le 0$) is **strictly barred** from reducing the SVI below the threshold dictated by the text evidence.

---

## 3. Counterfactual Explanation Engine

For every computed SVI, the platform generates dynamic counterfactual scenarios displayed in the **Evidence Inspector**:

$$\text{SVI}_{\text{counterfactual}} = \text{SVI}_{\text{current}} - \Delta_{\text{target\_evidence}}$$

### Example Auditor Display:
```text
Current SVI Score: 74 (Risk Band: HIGH)
Confidence: 0.88 | Policy Version: v2.1-PROVISIONAL-TRIAGE

Counterfactual Impact Analysis:
• Exclude Acoustic Supporting Evidence:  74 ──► 68 (-6 pts)
• Exclude Explicit Intimidation Marker:  74 ──► 51 (-23 pts)  [Band Shift: HIGH ──► MODERATE]
• Exclude Social Boycott Indicator:     74 ──► 64 (-10 pts)
```
This enables supervisors, auditors, and hackathon judges to verify that no single unvalidated model component exerts opaque control over triage outcomes.
