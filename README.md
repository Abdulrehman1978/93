# SAMBAL — Multilingual Trauma-Aware Intelligence & Response Layer (SIH26093)

> **SIH Problem Statement 26093:** AI-Based Real-Time Stress and Trauma Assessment Module for Victims/Complainants Accessing NHAA (14566) and Integrated Portal.  
> **Sponsoring Organization:** Ministry of Social Justice and Empowerment (MoSJE), Department of Social Justice and Empowerment (DoSJE).  
> **Architecture Baseline:** V3 Lean-Core Architecture.

---

## 1. Overview & Core Purpose

SAMBAL is a specialized trauma-aware intelligence-and-response layer designed to augment the **National Helpline Against Atrocities (NHAA - 14566)** ecosystem. It provides real-time multimodal distress detection, evidence-backed triage, and closed-loop multi-agency referral orchestration without replacing authorized human legal or clinical authorities.

### Core Pillars
1. **Immediate Safety Gate:** Zero-latency distress interrupt safeguarding citizens during acute crisis. Escalations to emergency response strictly enforce human-authorized handoff boundaries (`ERSS112Adapter`).
2. **Stress & Vulnerability Index (SVI 0–100):** Continuous trauma-informed composite scoring calibrated across acoustic features, linguistic distress markers, and situational vulnerability. Marked as `PROVISIONAL_TRIAGE_POLICY` pending Packet 11 calibration.
3. **Reported Incident Urgency:** Factual urgency classification based on reported narrative elements. The system identifies reported facts potentially relevant to urgency or statutory routing; it does **not** determine statutory guilt, crime occurrence, or complainant veracity.
4. **Evidence-First Inspector:** Preserves full evidentiary provenance (audio snippet timestamps, SNR quality, text spans, model confidence, policy versions, and human override logs).
5. **Closed-Loop Referral Tracking:** Tracks referrals through verifiable lifecycle states to verified agencies (Tele-MANAS `14416`, NALSA/DLSA legal aid, Sakhi One Stop Centres, ERSS `112`).

---

## 2. V3 Lean-Core Architecture

The system operates strictly on a unified, minimal-overhead production topology:

```text
Next.js PWA (apps/web)
      ↓ (REST / SSE / WebSocket)
FastAPI Modular Monolith (backend/app)
      ↓
Canonical PostgreSQL 16 (Port 5493)
      ↓
S3-Compatible Object Storage / MinIO (Port 9093)
      ↓
PostgreSQL-Backed Async Job Queue (SKIP LOCKED)
      ↓
External / Government Provider Adapters (Tele-MANAS, NALSA, ERSS 112)
```

> **Architectural Guardrail:** Redis, Celery, Kafka, RabbitMQ, Elasticsearch, and separate ML microservices are **prohibited** unless justified by measured hardware bottlenecks and formally approved via ADR.

---

## 3. Collision-Safe Local Port Configuration

To ensure zero port conflicts when running alongside existing local services:

| Component | Container Port | Host Port | Health Endpoint |
| :--- | :--- | :--- | :--- |
| **Next.js Web PWA** | `3000` | **`3093`** | `http://localhost:3093/api/health` |
| **FastAPI Backend** | `8000` | **`8093`** | `http://localhost:8093/health/live` |
| **Canonical PostgreSQL** | `5432` | **`5493`** | `pg_isready -p 5493` |
| **MinIO S3 API** | `9000` | **`9093`** | `http://localhost:9093/minio/health/live` |
| **MinIO Web Console** | `9001` | **`9193`** | `http://localhost:9193` |

---

## 4. Quickstart / Developer Bootstrap

### Prerequisites
- **Node.js:** `>= 20.x` (Recommended: `24.x`)
- **Python:** `>= 3.12.x`
- **uv:** `>= 0.4.x` (Recommended: `0.12.x`)
- **Docker & Docker Compose**

### Step-by-Step Local Setup

1. **Clone & Configure Environment:**
   ```bash
   cp .env.example .env
   ```

2. **Start Infrastructure Services (PostgreSQL & MinIO):**
   ```bash
   docker compose up -d db s3
   ```

3. **Install & Build Monorepo Dependencies:**
   ```bash
   # Install frontend & shared contracts dependencies
   npm install

   # Build shared contracts
   npm --workspace=packages/contracts run build

   # Set up backend virtual environment
   cd backend
   uv venv --python 3.12 .venv
   .venv\Scripts\activate
   uv pip install -e ".[dev]"
   cd ..
   ```

4. **Run Backend Service:**
   ```bash
   cd backend
   .venv\Scripts\uvicorn.exe app.main:app --port 8093 --reload
   ```

5. **Run Frontend Application:**
   ```bash
   npm --workspace=apps/web run dev
   ```

6. **Access Interfaces:**
   - Web Application: [http://localhost:3093](http://localhost:3093)
   - Interactive OpenAPI Docs: [http://localhost:8093/docs](http://localhost:8093/docs)
   - Backend Readiness Probe: [http://localhost:8093/health/ready](http://localhost:8093/health/ready)

---

## 5. Quality Gates & Validation Commands

### Backend Quality Gates
```bash
cd backend
.venv\Scripts\ruff.exe format --check .   # Formatter check
.venv\Scripts\ruff.exe check .            # Linter check (zero warnings)
.venv\Scripts\mypy.exe app                # Strict Python type check
.venv\Scripts\pytest.exe -v               # Unit & integration tests
```

### Frontend Quality Gates
```bash
npm run format:check                     # Prettier format check
npm run lint                             # Next.js ESLint
npm run typecheck                        # Strict TypeScript compilation
npm run test                             # Vitest unit smoke tests
npm run build                            # Production build
npm run test:e2e                         # Playwright E2E smoke tests
npm run test:a11y                        # Axe accessibility scan (zero violations)
```

---

## 6. Repository Structure

```text
c:\93/
├── .github/workflows/ci.yml       # GitHub Actions CI pipeline
├── apps/
│   └── web/                      # Next.js 14 PWA Client Shell
│       ├── src/app/              # App Router (Civic Calm layout, page, health route)
│       ├── tests/unit/           # Vitest unit smoke tests
│       ├── tests/e2e/            # Playwright E2E & Axe accessibility tests
│       └── Dockerfile            # Multi-stage production container
├── backend/                      # FastAPI Modular Monolith Shell
│   ├── app/                      # Application core (config, database, errors, logging)
│   │   ├── api/v1/health.py      # Liveness & readiness probes
│   │   └── intelligence/         # Abstract provider protocols (ASRProvider, etc.)
│   ├── tests/                    # Pytest suite (health, PII, config, contracts)
│   ├── Dockerfile                # Backend container definition
│   └── pyproject.toml            # Hatchling build & dependencies
├── packages/
│   └── contracts/                # Shared TypeScript & Zod schemas (@sambal/contracts)
├── docs/                         # Architecture, Research & Governance Documentation
│   ├── MASTER_PRODUCT_SPEC_V2.md # Authoritative product specification
│   ├── PROGRESS_TRACKER.md       # Packet status & audit tracking
│   └── results/                  # Packet outcome audit reports
├── docker-compose.yml            # Docker development orchestrator
└── package.json                  # Root monorepo workspace configuration
```

---

## 7. Architectural Decisions & Boundaries

- **ASR Baseline Candidate:** `faster-whisper-turbo + CTranslate2 INT8` is designated as `BASELINE_CANDIDATE`. Formal production selection requires Packet 08 benchmarking against Indic-focused/government alternatives (e.g. IndicConformer/Bhashini).
- **Canonical Database:** PostgreSQL 16+ is canonical across development integration, migrations, tests, E2E, CI, and production. SQLite is prohibited as a production or integration alternative.
- **Human-in-the-Loop Emergency Boundary:** `ERSS112Adapter` strictly requires human operator verification and authorization before dispatching external emergency handoffs.
- **PII-Safe Telemetry:** Logs automatically sanitize Aadhaar numbers, phone numbers, and email addresses via regex redaction filters before JSON formatting.
