# Container Architecture & C4 Level 2 Specification

> **Document ID:** ARCH-CONTAINER-DIAGRAM-V2  
> **Standard:** C4 Model — Level 2: Container Diagram  
> **Core Architectural Philosophy:** Modular Monolith over Microservices — Maximum Useful Capability, Minimum Operational Complexity.

---

## 1. Container Diagram (C4 Level 2)

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT SURFACES (NEXT.JS)                                    │
│                                                                                                 │
│  ┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────┐ │
│  │   Citizen PWA & Intake Portal                │  │   Operator Live Copilot & Admin Hub      │ │
│  │   • Voice, Text & Silent Intake Flows        │  │   • Real-Time WebSocket Waveform & Trans.│ │
│  │   • Civic Calm Accessible Design System      │  │   • Evidence Timeline & Inspector        │ │
│  │   • Granular DPDP Consent Center             │  │   • Referral Dispatcher & Resource Gaps  │ │
│  └──────────────────────┬───────────────────────┘  └─────────────────────┬────────────────────┘ │
└─────────────────────────┼────────────────────────────────────────────────┼──────────────────────┘
                          │ HTTPS / WSS                                    │ HTTPS / WSS
                          ▼                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI MODULAR HEADLESS INTELLIGENCE MONOLITH                         │
│                                                                                                 │
│  ┌───────────────────────────────────────┐      ┌────────────────────────────────────────────┐  │
│  │ API Gateway & Session Orchestrator    │      │ Multimodal Intelligence & Safety Core      │  │
│  │ • Channel Gateway (Web, Voice, Silent)│◄────►│ • Deterministic Safety Rule Engine         │  │
│  │ • DPDP Purpose-Scoped Consent Manager │      │ • Multilingual NLP Semantic Threat Engine  │  │
│  │ • RBAC & Audit Event Logger           │      │ • DSP Acoustic Feature Extractor (librosa) │  │
│  │ • Closed-Loop Referral State Machine  │      │ • SVI & Counterfactual Fusion Engine       │  │
│  └──────────────────┬────────────────────┘      └────────────────────┬───────────────────────┘  │
│                     │                                                │                          │
│                     │                                                ▼                          │
│                     │                           ┌────────────────────────────────────────────┐  │
│                     │                           │ Local Speech AI Engine                     │  │
│                     │                           │ • CTranslate2 faster-whisper-turbo         │  │
│                     │                           │ • WebRTC VAD Pause Detector                │  │
│                     │                           └────────────────────────────────────────────┘  │
│                     ▼                                                                           │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Government Integration & External Support Adapters                                        │  │
│  │ • TeleManasAdapter (MoHFW)  • LegalAidAdapter (NALSA)  • ERSS112Adapter  • SAMBALAdapter  │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────┬────────────────────────────────────────────────────────┬──────────────────┘
                      │                                                        │
                      ▼                                                        ▼
┌──────────────────────────────────────────────┐        ┌────────────────────────────────────────┐
│ Relational Database (PostgreSQL 16)          │        │ S3-Compatible Storage (MinIO / AWS S3) │
│ • 34 Normalized Domain Tables (Budget ≤ 45)  │        │ • Ephemeral session audio buffers      │
│ • Cases, Consents, Evidence, Referrals, SVI  │        │ • Strict 90-day automated purge policy │
│ • ACID Transactions, Row-Level RBAC          │        │ • Server-side AES-256 encryption       │
└──────────────────────────────────────────────┘        └────────────────────────────────────────┘
```

---

## 2. Container Responsibility & Communication Contracts

| Container Name | Technology Stack | Primary Operational Responsibility | Communication Protocols & Interfaces |
| :--- | :--- | :--- | :--- |
| **Citizen PWA & Intake Portal** | Next.js 14/15, React, Tailwind CSS, Lucide Icons | Responsive mobile-first interface for complainants. Provides Speak, Write, and Silent flows; Quick Exit; Consent Center. | HTTPS REST API & WebSocket to FastAPI Gateway. |
| **Operator Live Copilot & Admin Hub** | Next.js, Web Audio API, Canvas Waveform | High-density desktop workspace for 14566 operators, supervisors, and ministry officials. Visualizes synchronized timeline, evidence, and referrals. | Persistent WSS connection for streaming audio tokens and real-time alerts. |
| **FastAPI Modular Monolith** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2 | Houses all business logic, session orchestration, consent enforcement, referral state machines, and adapter gateways. | Exposes versioned OpenAPI 3.1 endpoints (`/api/v1/*`) and WebSocket handlers (`/ws/*`). |
| **Local Speech AI Engine** | CTranslate2, `faster-whisper-turbo`, WebRTC VAD | Performs sub-second streaming transcription and pause boundary detection entirely in-process on CPU/GPU. | Python In-Process Memory Protocol via `SpeechToTextProvider`. |
| **Relational Database** | PostgreSQL 16+ (or local SQLite for zero-config demo) | Stores structured case records, transcripts, evidence items, SVI results, referrals, and audit trails. | Parameterized async SQL via SQLAlchemy v2 & asyncpg. |
| **Object Storage** | MinIO / S3 Standard | Temporarily holds audio chunks during active streaming sessions. Employs immediate cryptographic deletion upon session closure. | S3 REST API via `boto3` / `aioboto3`. |
