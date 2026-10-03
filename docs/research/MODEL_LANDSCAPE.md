# Multilingual Speech, NLP & Affective Model Landscape Evaluation

> **Document ID:** MODEL-LANDSCAPE-EVAL-V2  
> **Topic:** Evaluation of ASR, NLP, Acoustic Analytics, and Affective Signal Models for Indian Crisis Helpline Telephony  
> **Date:** October 2026  
> **Evaluation Dimensions:** Accuracy, Indian Language & Code-Switching Coverage, Latency (CPU vs GPU), Telephone Audio Robustness, Offline Feasibility, Licensing

---

## 1. Speech-to-Text (ASR) Candidate Evaluation

Crisis intake over **14566** involves 8kHz narrowband PSTN telephone audio or variable-bandwidth mobile VoIP audio, spoken with regional dialects and heavy code-switching (e.g., Hindi-English, Marathi-Hindi-English).

| Model Candidate | Developer / Provider | Architecture | Indian Language Coverage | Code-Switching Quality | 8kHz Telephone Audio Robustness | Latency Profile | Offline / Edge Feasibility | License | Assessment & Deployment Tier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **faster-whisper** (`large-v3` / `turbo`) | SYSTRAN / OpenAI | CTranslate2-optimized Transformer Encoder-Decoder | Strong across major Indian languages (hi, mr, bn, ta, te, kn, gu, pa, ur, en). | Moderate-to-High; handles natural Hinglish well; may occasionally normalize loanwords. | Moderate; requires audio resampling and high-pass filtering to mitigate low-band loss. | Measured in dev (~1.1s on 4-core CPU for 5s chunk with `turbo`). Latency varies with SNR. | Excellent; self-contained binary, zero external network dependency. | MIT | **BASELINE_CANDIDATE (Initial Local Implementation)** |
| **AI4Bharat IndicConformer** | AI4Bharat / IIT Madras | Conformer ASR trained on 10,000+ hours of Indic speech | Exceptional across 22 scheduled Indian languages. | **Best-in-class** for authentic Indian accents and dialectal variations. | High; trained on diverse real-world Indian acoustic environments. | Moderate on CPU; optimal on CUDA/TensorRT (~400ms per utterance on T4). | Feasible with ONNX / PyTorch deployment; requires ~2GB model weights. | MIT | **EVALUATION CANDIDATE (Packet 08 Benchmark)** |
| **BHASHINI ASR Gateway** | Digital India Bhashini Division (MeitY) | Multi-model national language pipeline | Full 22 official Indian languages. | Very High for regional colloquial speech. | High; tuned on national public service datasets. | Dependent on government network gateway latency (~800ms - 2.5s network roundtrip). | Cloud-only; requires MeitY API key and authorization. | Government API Terms | **OFFICIAL GOV CANDIDATE (ADAPTER_READY)** |
| **OpenAI Whisper API / Commercial Cloud** | OpenAI / Azure / Google Cloud STT | Proprietary cloud endpoints | Broad multilingual coverage. | High. | High with automatic audio pre-filtering. | 1.0s - 2.0s network latency; recurring token and per-minute costs ($0.006/min). | None; violates air-gapped or localized public-sector data residency requirements. | Commercial SaaS | **SANDBOX / BACKUP ONLY** |

### Selected ASR Strategy & Benchmark Mandate
- **Baseline Candidate:** `faster-whisper-turbo` (CTranslate2 INT8 quantization) running locally in the backend worker container. It serves as the initial local development baseline. It is **NOT** a finalized production selection, and sub-second streaming latency is an aspirational design target subject to real hardware validation.
- **Provider Abstraction:** Implemented strictly via the `ASRProvider` protocol interface. Domain and safety logic must never directly couple to CTranslate2 or any specific speech vendor.
- **Packet 08 Benchmarking Mandate:** Final production ASR selection will be decided during Packet 08 by benchmarking the baseline candidate against at least one viable Indic-focused or government alternative (AI4Bharat IndicConformer / Bhashini) on:
  1. Word Error Rate (WER) across Hindi, Indian English, Marathi, Bengali, Tamil, Telugu
  2. Critical safety phrase recall (threats, self-harm keywords, weapon mentions)
  3. Code-switching performance (Hinglish, Marathlish)
  4. Telephone-quality audio degradation (8kHz downsampled audio)
  5. Background noise resilience (street, vehicle, and household noise)
  6. CPU vs. GPU latency profiles
  7. Time-to-first-partial and Time-to-stable-segment
  8. End-to-end safety-alert latency
  9. Memory footprint and peak RAM
  10. Operating cost and licensing compatibility
  11. Offline and air-gapped viability
All latency and throughput claims must be backed by measured hardware/environment evidence.

---

## 2. Text NLP, Threat Detection & Safety Candidates

| Model / Approach | Scope / Task | Latency | Language Support | Explainability | Failure Modes | Role in Architecture |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Deterministic Multilingual Safety Rules (Regex + Lexicon)** | Immediate violence, weapons, explicit self-harm, coercion, caste slurs under PoA Act. | **< 1ms** | Pre-compiled multilingual lexicons (en, hi, mr, bn, ta, te). | **100% Deterministic** (Outputs exact matched span, rule ID, and statutory cross-reference). | Vulnerable to creative spelling, evasion, and complex double negations. | **LAYER 1: NON-NEGOTIABLE SAFETY GATE** |
| **MuRIL** (*Multilingual Representations for Indian Languages*) | Cross-lingual embedding & semantic classification (Google Research). | ~15ms on CPU (ONNX) | 17 Indian languages + English; pretrained on monolingual, translated, and transliterated pairs. | High when paired with Attention weight inspection and prototype distance. | Requires fine-tuning on labeled domain corpus. | **LAYER 2: SEMANTIC THREAT & VULNERABILITY CLASSIFIER** |
| **IndicBERT v2** | Masked LM for Indic NLP (AI4Bharat). | ~20ms on CPU | 22 Indian languages. | Good attention visualization. | Sentence length limitations; sensitive to noisy ASR tokens. | **BENCHMARK ALTERNATIVE (LAYER 2)** |
| **Structured LLM Reasoner** (e.g., Llama-3-8B-Instruct quantized / Gemini API / Claude) | Complex contextual extraction, temporal disambiguation, multi-hop intimidation analysis. | 600ms - 1800ms | Multilingual comprehension; excellent nuance detection. | Moderate (can provide textual chain-of-thought justifications; vulnerable to subtle hallucinations). | Cloud outage, prompt injection, latency spikes, token economics. | **LAYER 3: CONTEXTUAL COGNITION (DEGRADABLE)** |

### Multi-Layer Safety Architecture (Rule-Guided Defense)
To satisfy the strict safety mandates of SIH26093:
- **Layer 1 (Deterministic Rules):** Evaluates immediately upon receiving ASR transcript chunks. If explicit self-harm or active violence is detected, it triggers the **Immediate Safety Gate** instantaneously, bypassing slower LLM reasoning.
- **Layer 2 (Semantic Classifier):** Disambiguates negation, reported speech, and indirect threats.
- **Layer 3 (Contextual LLM Reasoner):** Synthesizes multi-turn case context and populates structured JSON schemas with full Pydantic validation.
- **Layer 4 (Human Operator Oversight):** Final verification and authorization by the human operator.

---

## 3. Speech Analytics & Affective Signal Engine

### Acoustic Feature Extraction Pipeline
Rather than relying on black-box emotion classifiers, we compute transparent, mathematically defined digital signal processing (DSP) parameters:
1. **Voice Activity & Segmentation:** WebRTC VAD (Voice Activity Detection) to isolate speech segments from background telephone noise.
2. **Pitch (F0) Dynamics:** Monitored via the `pyin` (Probabilistic YIN) algorithm. Measures:
   - Mean F0, Standard Deviation of F0.
   - Micro-pitch tremor and sudden octave jumps indicating vocal fold tension.
3. **Pause Architecture:**
   - Hesitation Ratio = Total Silence Time / Total Duration.
   - Long Pause Count (pauses > 1.8 seconds).
   - Abrupt Pause Bursts during sensitive disclosure.
4. **Speech Rate (Syllable Tempo):** Syllable peaks per second calculated from spectral flux and envelope intensity.
5. **Energy & Vocal Stability:**
   - Root Mean Square (RMS) energy shifts.
   - Shimmer and Jitter approximations for vocal strain.
6. **Audio Quality Index (AQI):**
   - Signal-to-Noise Ratio (SNR in dB).
   - Frequency band verification (flags 8kHz telephone roll-off vs 16kHz wideband).

### Bounded Affective AI Policy
- **Model:** `wav2vec2-xlsr-53` or specialized prosodic classifier mapped to 5 observable distress states:
  - `ELEVATED_AROUSAL_SIGNAL`
  - `FEAR_ASSOCIATED_ACOUSTIC_SIGNAL`
  - `DISTRESS_ASSOCIATED_SIGNAL`
  - `FLAT_AFFECT_SIGNAL` (Dissociation / Exhaustion)
  - `BASELINE_STABLE`
- **Bounded Influence Rule:** The Affective Signal Engine can adjust the Stress Vulnerability Index by at most **±15 points**. It can **NEVER** downgrade an explicit threat of violence or override a self-harm statement.
- **Abstention Policy:** If the Audio Quality Index indicates an SNR < 12dB or severe telephone clipping, the affective engine outputs `LOW_AUDIO_QUALITY_ABSTAIN` and downstream confidence intervals widen accordingly.
