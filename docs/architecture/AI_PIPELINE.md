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
├── faster-whisper-turbo (BASELINE_CANDIDATE ASR)       ├── Layer 1: Deterministic Safety Rules
└── Affective Distress Classifier (Bounded ±15)         ├── Layer 2: Semantic Threat Classifier
         │                                              └── Layer 3: Contextual Extraction
         └───────────────────────────┬───────────────────────────┘
                                     │
                                     ▼
                      [ MULTIMODAL EVIDENCE FUSION ]
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
[ 1. IMMEDIATE SAFETY GATE ]  [ 2. STRESS VULNERABILITY ]  [ 3. REPORTED INCIDENT URGENCY ]
├── Physical Assault Threat   ├── SVI: 0–100              ├── Reported Threat / Harm Facts
├── Active Weapons Nearby     ├── Policy: PROVISIONAL     ├── Time-Sensitive Legal Deadlines
├── Present Self-Harm Intent  │   • LOW (0–29)            ├── Vulnerable Dep. (Kids/Elderly)
└── OVERRIDE: CRITICAL ALERT  │   • MODERATE (30–59)      └── Independent of voice calmness
                              │   • HIGH (60–84)              (Does NOT determine guilt)
                              │   • CRITICAL (85–100)
                              └── Contribution Breakdown
                                     │
                                     ▼
                    [ SUPPORT RECOMMENDATION ENGINE ]
                    ├── Tele-MANAS Counseling
                    ├── DLSA Legal Aid (Section 15A)
                    ├── Police Atrocity Protection Cell (Human Authorized)
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

---

## 4. AI Provider Boundaries & Protocol Contracts

To decouple domain workflows from third-party vendor churn and enable seamless model benchmarking, all intelligence layers interact strictly through abstract protocols:

```python
# app/intelligence/contracts.py

class ASRProvider(Protocol):
    """Streaming and batched speech-to-text transcription interface."""
    async def transcribe_stream(self, audio_chunk: bytes, language: Optional[str]) -> TranscriptSegment: ...

class LanguageDetectionProvider(Protocol):
    """Detects spoken and written language and code-switching tokens."""
    async def detect_language(self, text_or_audio: Any) -> LanguageConfidence: ...

class TranslationProvider(Protocol):
    """Normalizes vernacular narratives into canonical representations."""
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> TranslatedText: ...

class TextSafetyProvider(Protocol):
    """Executes deterministic and semantic safety classification."""
    async def evaluate_safety(self, text: str, context: SessionContext) -> TextSafetyEvaluation: ...

class ContextExtractionProvider(Protocol):
    """Extracts structured entities, threats, and structural vulnerabilities."""
    async def extract_context(self, text: str) -> StructuredNarrativeContext: ...

class AcousticFeatureProvider(Protocol):
    """DSP feature extraction (F0, RMS energy, speech rate, pause statistics)."""
    async def extract_features(self, audio_buffer: np.ndarray, sample_rate: int) -> AcousticFeatureVector: ...

class AffectiveSignalProvider(Protocol):
    """Auxiliary prosodic distress classification with bounded influence."""
    async def infer_affective_signal(self, acoustic_features: AcousticFeatureVector) -> AffectiveSignalResult: ...

class LLMProvider(Protocol):
    """Contextual narrative synthesis and structured JSON generation."""
    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel: ...
```

### Architectural Guardrails:
1. **SDK Decoupling:** Business and domain logic must NEVER directly import or depend on a specific external model SDK (e.g. `google.generativeai`, `openai`, or `ctranslate2`). All model interaction passes through these interfaces.
2. **Provisional SVI Policy:** In accordance with the pre-Packet 01 architectural lock, `SVI_POLICY_STATUS = PROVISIONAL_TRIAGE_POLICY`. Final formula weights belong to Packet 11 after empirical evaluation in Packets 08–10.
3. **Evidence-First Domain Rule:** The authoritative database and domain record must never be reduced to a single score. The system must perpetually preserve:
   `assessment`, `immediate_safety_result`, `svi_result`, `reported_incident_urgency`, `evidence_items[]`, `model_runs[]`, `policy_version`, `confidence`, `quality_flags[]`, `human_review_status`, and `operator_override`.
