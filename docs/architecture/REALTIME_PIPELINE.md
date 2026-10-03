# Real-Time Streaming & Audio Pipeline Architecture

> **Document ID:** ARCH-REALTIME-PIPELINE-V2  
> **Topic:** Sub-Second Audio Streaming, DSP Extraction, and Real-Time Event Synchronization  
> **Target Latency Budget:** End-to-end token latency < 1.2s; Alert broadcast latency < 250ms

---

## 1. Real-Time Telemetry & Transport Pipeline

```text
[ Browser / Telephony SIP Trunk ]
          │ (Raw PCM / Opus audio chunks, 500ms windows)
          ▼
[ WebSocket Endpoint: `/ws/v1/sessions/{id}/audio` ]
          │
          ├──► In-Memory Ring Buffer (Holds rolling 10s of audio)
          │
          ├──► WebRTC VAD (Voice Activity Detection, 30ms frames)
          │    ├── Speech Frame: Accumulate into Speech Segment Buffer
          │    └── Silence Frame: If silence > 1.8s, trigger Pause Event
          │
          ├──► DSP Feature Extractor (Parallel thread pool)
          │    ├── F0 Pitch Calculation (pyin)
          │    ├── RMS Energy & Shimmer
          │    └── Emission: `ACOUSTIC_PROSODIC_METRICS` event
          │
          └──► Audio Quality Monitor
               └── Computes SNR; flags `LOW_AUDIO_QUALITY` if SNR < 10dB
          │
[ ASR Streaming Inference (Every 2.0s of continuous speech) ]
          │
          ▼
[ `faster-whisper-turbo` (CTranslate2 INT8) ]
          │
          ├── Emits `PARTIAL_TRANSCRIPT` (displayed in gray on Operator UI)
          └── Emits `FINAL_TRANSCRIPT_SEGMENT` (with word-level timestamps)
          │
          ▼
[ Real-Time Safety & Threat Evaluator ]
          │ (Executes in < 5ms over transcript segment)
          │
          ├── Deterministic Safety Regex Match?
          │   ├── YES ──► Broadcast `IMMEDIATE_SAFETY_ALERT` via WebSocket (HIGH PRIORITY)
          │   └── NO  ──► Enqueue for Semantic Threat Classifier
          │
          ▼
[ Operator Live Copilot WebSocket (`/ws/v1/operator/sessions/{id}`) ]
          ├── Appends text to Live Transcript Pane
          ├── Draws waveform segment on Canvas
          ├── Pins Evidence Marker to synchronized Timeline
          └── Updates SVI Gauge and Suggested Next Questions
```

---

## 2. Latency Budget & Concurrency Engineering

| Pipeline Stage | Target Latency Budget | Maximum Permissible Latency | Optimization Strategy |
| :--- | :--- | :--- | :--- |
| **Audio Chunk Ingest** | 50ms | 100ms | Async WebSocket frame reading without blocking event loop. |
| **WebRTC VAD & Segmentation** | 10ms | 25ms | Native C-extension execution over 30ms audio windows. |
| **DSP Acoustic Feature Extraction** | 80ms | 150ms | Offloaded to background thread pool; downsampled calculation. |
| **ASR Chunk Decoding** | 800ms | 1200ms | CTranslate2 INT8 quantization; beam size = 1; local CPU/GPU execution. |
| **Deterministic Safety Check** | 2ms | 10ms | Pre-compiled regex automata evaluated on incoming segment text. |
| **Semantic NLP Threat Evaluation** | 40ms | 120ms | Local ONNX transformer model inference; batched sentence embeddings. |
| **Evidence Fusion & SVI Calculation** | 5ms | 15ms | In-memory mathematical evaluation of weighted evidence vectors. |
| **WebSocket Operator Broadcast** | 15ms | 50ms | Binary/JSON WebSocket frame push over local loopback / high-speed LAN. |
| **Total Real-Time Pipeline Latency** | **~1002ms (~1.0s)** | **< 1670ms (< 1.7s)** | **Full sub-second to near-real-time streaming delivery** |

---

## 3. Backpressure & Degradation Protocol
1. **Network Buffer Surges:** If client WebSocket buffer fills beyond 5MB, system pauses non-critical acoustic metric streaming and prioritizes transcript text and Immediate Safety alerts.
2. **Audio Packet Loss:** If packet loss exceeds 20%, system marks incoming audio segment with `AUDIO_DEGRADED` flag and widens SVI confidence interval without crashing the session.
3. **Reconnection Grace Period:** If the operator or citizen drops connection, the session ring buffer persists state for 60 seconds, allowing instant re-attachment without losing in-flight transcript.
