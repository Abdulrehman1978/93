# End-to-End Data Flow Architecture

> **Document ID:** ARCH-DATA-FLOW-V2  
> **Topic:** Real-Time Data Flow: From First Signal to Verified Support  
> **Standard:** Complete Provenance, Auditable Transformations, and DPDP-Compliant Purpose Boundaries

---

## 1. End-to-End Data Flow Diagram

```text
[ CITIZEN CONTACT ]
(Voice 14566 / Text / Silent)
       │
       ▼
[ STEP 1: CHANNEL GATEWAY & CONSENT VALIDATION ]
├── Validates active channel (Voice, Web, Silent)
├── Checks & registers granular consent (Transcription, AI Assessment, Referral Sharing)
└── Generates cryptographically signed, purpose-limited `SessionContext`
       │
       ▼
[ STEP 2: STREAM SPLITTER & PIPELINE DISPATCH ]
├── Audio Stream ──────────────────────────────────────────┐
│   ├── Audio Buffer (In-memory ring buffer)               │
│   ├── WebRTC VAD (Pause & speech segment detection)      │
│   └── DSP Feature Extractor (F0, RMS, Shimmer, Rate)     │
│                                                          │
│   Text / Transcribed Chunks ◄────────────────────────────┘
│   ├── Language & Code-Switch Detection
│   └── Normalization (Script preservation + transliteration)
       │
       ▼
[ STEP 3: MULTI-LAYER SAFETY & THREAT EVALUATION ]
├── Layer 1: Deterministic Multilingual Regex (Imminent Self-Harm, Active Weapons, Severe Threats)
│   └── IF CRITICAL SAFETY MATCH ──► [ INSTANT IMMEDIATE SAFETY ALERT OVERRIDE ]
├── Layer 2: Semantic Threat Classifier (Intimidation, Coercion, Social Boycott, Negation Handling)
└── Layer 3: Contextual Narrative Reasoner (Multi-hop structural vulnerability & dependency)
       │
       ▼
[ STEP 4: EVIDENCE REGISTRATION & ATTRIBUTION ]
├── Each detected indicator creates an immutable `EvidenceItem`:
│   { evidence_id, modality, timestamp_start, timestamp_end, raw_snippet, confidence, model_version }
       │
       ▼
[ STEP 5: MULTIMODAL FUSION & TRIAGE SCORING ]
├── 1. Immediate Safety Gate (NO_IMMEDIATE_SIGNAL | REVIEW_RECOMMENDED | ELEVATED | CRITICAL_REVIEW)
├── 2. Stress Vulnerability Index (SVI: 0–100, Configurable Policy Bands: LOW, MOD, HIGH, CRITICAL)
└── 3. Incident Urgency (Statutory PoA severity independent of acoustic distress)
       │
       ▼
[ STEP 6: REAL-TIME WEBSOCKET BROADCAST ]
├── Dispatched to Operator Live Copilot (`/operator/live/[sessionId]`)
├── Renders synchronized Waveform, Transcript, and Evidence Pins in < 250ms
└── Emits trauma-informed `SuggestedPrompt` based on missing information
       │
       ▼
[ STEP 7: HUMAN OPERATOR OVERSIGHT & DECISION ]
├── Operator accepts, modifies, or overrides SVI and Urgency
├── Operator approves recommended support pathways (e.g., Tele-MANAS, DLSA Legal Aid)
└── System logs operator feedback and justification for future calibration
       │
       ▼
[ STEP 8: SAFE HANDOFF & CLOSED-LOOP REFERRAL DISPATCH ]
├── System packages minimal, consented `SafeHandoffPayload` ("Share Less" principle)
├── Dispatched via Adapter (`TeleManasAdapter`, `LegalAidAdapter`, `ERSS112Adapter`)
└── Initiates Closed-Loop Referral Lifecycle (REFERRED → ACKNOWLEDGED → CONTACTED → SUPPORT_STARTED)
       │
       ▼
[ STEP 9: OUTCOME LOGGING & PRIVACY CLOSURE ]
├── Session audio buffer purged from memory (Ephemeral Audio Policy)
├── Case docket and referral state synchronized with SAMBAL core
└── Complainant notified via SMS / PWA Case Tracker
```

---

## 2. Immutable Evidence Item Schema Contract

Every consequential decision in the data pipeline is anchored to an explicit, typed evidence object:

```python
class EvidenceItem(BaseModel):
    evidence_id: UUID
    assessment_id: UUID
    modality: Literal["ACOUSTIC", "TEXT_TRANSCRIPT", "TYPED_INPUT", "SILENT_TAP", "CONTEXTUAL"]
    signal_type: Literal[
        "IMMINENT_SELF_HARM",
        "EXTERNAL_THREAT",
        "COERCION_RETALIATION",
        "SOCIAL_BOYCOTT",
        "SEVERE_DISTRESS_ACOUSTIC",
        "PROLONGED_HESITATION_PAUSE",
        "DISPLACEMENT_ISOLATION",
        "PHYSICAL_INJURY_MEDICAL"
    ]
    timestamp_start_ms: int
    timestamp_end_ms: int
    raw_snippet: str
    confidence: float = Field(ge=0.0, le=1.0)
    audio_quality_snr: Optional[float] = None
    model_version: str
    svi_point_contribution: float
    human_review_status: Literal["PENDING", "CONFIRMED", "DISMISSED", "MODIFIED"] = "PENDING"
    created_at: datetime
```
