# ADR-001: Headless Modular Monolith with In-Process Speech AI over Distributed Microservices

> **Status:** ACCEPTED  
> **Date:** October 2026  
> **Deciders:** Principal Architect, Staff Systems Engineer, DevSecOps Lead  
> **Technical Scope:** Core Application Architecture & Deployment Topology

---

## 1. Context & Problem Statement

The **SIH26093** challenge demands an enterprise-grade, real-time stress and trauma intelligence layer capable of handling streaming audio, multilingual NLP, and closed-loop support orchestration for the National Helpline Against Atrocities (14566).

Teams often gravitate toward distributed microservices (deploying separate services for ASR, emotion analysis, database, NLP, and dispatch connected via Kafka/RabbitMQ and orchestrated via Kubernetes). However, in high-stakes public sector crisis infrastructure:
1. **Network Serialization Overhead:** Passing streaming 500ms audio chunks across multiple internal network hops introduces 200–500ms of inter-service network serialization latency, violating the < 1.2s total streaming latency budget.
2. **Operational Fragility:** A 10-microservice cluster introduces multiple points of network and container failure, complicated secret management, and significant memory overhead (> 16GB RAM baseline).
3. **Government Deployment Barriers:** District call centers and NIC state nodes require predictable, low-complexity deployment footprints that can run on standard government VMs without requiring a dedicated Kubernetes SRE team.

---

## 2. Decision

We choose a **Headless Modular Monolith** built on **FastAPI (Python 3.12+)** and **Next.js (App Router)**:

1. **In-Process Speech AI & DSP:** The speech-to-text engine (`faster-whisper-turbo` via CTranslate2 INT8) and acoustic feature extractors (`librosa`, WebRTC VAD) execute directly in-process within the backend application worker pool, reading from shared memory ring buffers with zero inter-process network overhead.
2. **Headless Module-First Design:** All intelligence, safety, scoring, and orchestration logic is exposed via clean, versioned REST (`/api/v1/*`) and WebSocket (`/ws/v1/*`) contracts. The Next.js frontend is a reference consumer; any external portal (14566 telephony, SAMBAL portal, mobile app) can integrate directly via headless APIs.
3. **Database Budget:** Single relational PostgreSQL 16 instance with $\le 45$ normalized domain tables.
4. **Lean Background Tasks:** Async background tasks and referral webhook retries are managed via native asyncio worker queues backed by database transactional locking, eliminating external Redis/Celery dependencies for the default deployment.

---

## 3. Consequences & Trade-Offs

### Positive Consequences
- **Ultra-Low Latency:** Zero inter-service serialization overhead enables streaming ASR + DSP + safety evaluation in under 1.1s.
- **One-Command Bootstrap:** Entire platform boots via `docker-compose up` or native local virtual environment with zero external message broker prerequisites.
- **Strict Domain Boundaries:** Code is cleanly partitioned into modular domain packages (`app.intelligence`, `app.safety`, `app.referral`, `app.integrations`) preserving microservice modularity without microservice operational tax.
- **Air-Gap & Offline Resilience:** Easily packagable as a self-contained container for classified or air-gapped government environments.

### Negative Consequences & Mitigations
- *Consequence:* Scaling requires scaling the entire monolith rather than individual model workers.
- *Mitigation:* The monolith is strictly stateless; session state is maintained in PostgreSQL and ephemeral memory buffers. Multiple instances can be deployed behind a standard Nginx / HAProxy load balancer with sticky WebSocket sessions.
