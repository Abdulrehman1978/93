# Packet 01 — Repository Foundation & Monorepo Toolchain: Result Report

> **Packet ID:** PKT-01  
> **Status:** `PASS`  
> **Date:** 2026-10-03  
> **Author:** DevSecOps / Staff Systems Engineer  
> **Reviewed By:** Principal System Architect  
> **Repository Baseline:** SAMBAL Monorepo (SIH26093)  

---

## 1. Status

`PASS`

All required foundation scopes, strict type safety contracts, linting, formatting, unit/E2E/a11y tests, container definitions, and CI pipelines have been implemented and verified with zero warnings, zero errors, and zero accessibility violations.

---

## 2. Scope Executed

Packet 01 established the repository baseline and toolchain foundation under the V3 Lean-Core Architecture without premature substantive domain logic:
1. **Repository & Monorepo Workspace Structure:**
   - Root npm workspace orchestrating `apps/*` and `packages/*`.
   - `.gitignore`, `.dockerignore`, `.env.example`, `.env`.
   - Dedicated `backend` FastAPI service with Hatchling build and virtual environment management via `uv`.
2. **Next.js PWA Application Shell (`apps/web`):**
   - Next.js 14 App Router with Civic Calm theme tokens (`tailwind.config.ts`, `globals.css`).
   - Accessible, semantic layout (`lang="en"`, skip to content, single `<h1>` hierarchy, high-contrast palette meeting WCAG 2.1 AA).
   - Dedicated health endpoint (`/api/health`) conforming to `@sambal/contracts`.
3. **FastAPI Modular Monolith Shell (`backend`):**
   - Modular application architecture (`app/config.py`, `app/database.py`, `app/storage.py`, `app/logging.py`, `app/errors.py`, `app/main.py`).
   - Strict Pydantic Settings validating environment configuration and enforcing PostgreSQL canonical driver (`postgresql+asyncpg://`).
   - Structured JSON logging with request correlation IDs and zero-leakage PII redaction (Aadhaar, Indian mobile phones, emails).
   - RFC 7807 Problem Details error handler returning `application/problem+json`.
   - Kubernetes/Docker liveness (`/health/live`) and readiness (`/health/ready`) probes evaluating live PostgreSQL and S3 dependencies.
4. **Shared Contract Strategy (`packages/contracts`):**
   - TypeScript library with Zod schemas and inferenced types for `HealthStatus`, `ProblemDetails`, `ImmediateSafetyState`, `SVIBand`, `ReportedUrgencyLevel`, `EvidenceItem`, `FollowUpPolicy`, and `ReferralState`.
5. **Abstract Intelligence Boundaries (`backend/app/intelligence/contracts.py`):**
   - Pure typing protocols enforcing that domain logic does not import vendor SDKs directly (`ASRProvider`, `LanguageDetectionProvider`, `TranslationProvider`, `TextSafetyProvider`, `ContextExtractionProvider`, `AcousticFeatureProvider`, `AffectiveSignalProvider`, `LLMProvider`).
   - Codified `faster-whisper-turbo` as `BASELINE_CANDIDATE` pending Packet 08 benchmarking.
6. **Container & Infrastructure Orchestration (`docker-compose.yml`):**
   - PostgreSQL 16 container (`sambal-db`) on host port `5493`.
   - MinIO S3 container (`sambal-s3`) on host API port `9093`, console port `9193`.
   - Backend container (`sambal-backend`) on host port `8093`.
   - Frontend container (`sambal-web`) on host port `3093`.
   - Verified collision-safe coexistence with existing system services on ports 5432/8000/3000.
7. **CI Pipeline & Quality Harness:**
   - GitHub Actions workflow (`.github/workflows/ci.yml`) covering backend quality gates, frontend quality gates, and security secret scanning.
   - Comprehensive test harnesses: Pytest, Vitest, Playwright, and `@axe-core/playwright`.

---

## 3. Files Created and Modified

```text
c:\93/
├── .dockerignore                           [CREATED] Docker build ignore patterns
├── .env.example                            [CREATED] Validated environment configuration template
├── .env                                    [CREATED] Local development environment config (port 5493/8093/3093/9093)
├── .gitignore                              [CREATED] Git ignore rules for node, python, venv, and build artifacts
├── docker-compose.yml                      [CREATED] Multi-container orchestration (PostgreSQL, MinIO, Backend, Web)
├── package.json                            [CREATED] Root npm workspace definitions and monorepo scripts
├── README.md                               [CREATED] Developer setup, architecture boundaries, ports, and verification
├── .github/
│   └── workflows/
│       └── ci.yml                          [CREATED] Multi-job CI workflow (backend, frontend, security)
├── packages/
│   └── contracts/
│       ├── package.json                    [CREATED] @sambal/contracts package configuration
│       ├── tsconfig.json                   [CREATED] TypeScript compiler configuration for declarations
│       └── src/
│           └── index.ts                    [CREATED] Zod schemas & TypeScript types for SAMBAL contracts
├── backend/
│   ├── pyproject.toml                      [CREATED] Hatchling build, dependencies, ruff, mypy, pytest config
│   ├── requirements-lock.txt               [CREATED] Frozen Python dependency lockfile
│   ├── README.md                           [CREATED] Backend development guide
│   ├── Dockerfile                          [CREATED] Multi-stage slim container definition
│   ├── app/
│   │   ├── __init__.py                     [CREATED] Backend app package marker
│   │   ├── config.py                       [CREATED] Pydantic Settings & environment validation
│   │   ├── database.py                     [CREATED] Canonical PostgreSQL async engine & health check
│   │   ├── storage.py                      [CREATED] S3 / MinIO storage provider & health check
│   │   ├── logging.py                      [CREATED] Structured JSON logging & PII redaction filter
│   │   ├── errors.py                       [CREATED] RFC 7807 Problem Details model & exception handlers
│   │   ├── main.py                         [CREATED] FastAPI application shell, CORS, correlation middleware
│   │   ├── api/
│   │   │   ├── __init__.py                 [CREATED] API router package
│   │   │   └── v1/
│   │   │       ├── __init__.py             [CREATED] API v1 router package
│   │   │       └── health.py               [CREATED] Liveness (/health/live) and readiness (/health/ready) probes
│   │   └── intelligence/
│   │       ├── __init__.py                 [CREATED] Intelligence package
│   │       └── contracts.py                [CREATED] Abstract provider boundary protocols (ASRProvider, etc.)
│   └── tests/
│       ├── conftest.py                     [CREATED] Pytest fixtures & async test client
│       ├── test_config.py                  [CREATED] Settings & PostgreSQL validation tests
│       ├── test_logging_pii.py             [CREATED] Aadhaar, phone, and email PII redaction tests
│       ├── test_health.py                  [CREATED] Liveness, readiness, and RFC 7807 error tests
│       └── test_intelligence_contracts.py  [CREATED] Protocol conformance & runtime checkability tests
├── apps/
│   └── web/
│       ├── package.json                    [CREATED] @sambal/web package, scripts, dependencies
│       ├── tsconfig.json                   [CREATED] Strict TypeScript Next.js configuration
│       ├── next.config.mjs                 [CREATED] Next.js configuration with transpiled packages
│       ├── tailwind.config.ts              [CREATED] Civic Calm theme tokens (WCAG AA compliant contrast)
│       ├── postcss.config.mjs              [CREATED] PostCSS tailwindcss & autoprefixer config
│       ├── .eslintrc.json                  [CREATED] ESLint Next.js Core Web Vitals config
│       ├── vitest.config.ts                [CREATED] Vitest unit test configuration
│       ├── playwright.config.ts            [CREATED] Playwright E2E and webServer configuration
│       ├── Dockerfile                      [CREATED] Multi-stage production container
│       ├── public/
│       │   └── robots.txt                  [CREATED] Public assets placeholder
│       ├── src/
│       │   └── app/
│       │       ├── globals.css             [CREATED] Base Tailwind styles & background tokens
│       │       ├── layout.tsx              [CREATED] Civic Calm layout, a11y skip-link, header & footer
│       │       ├── page.tsx                [CREATED] Foundation dashboard, 3D risk pillars, single h1
│       │       └── api/
│       │           └── health/
│       │               └── route.ts        [CREATED] Next.js health endpoint conforming to HealthStatus
│       └── tests/
│           ├── setup.ts                    [CREATED] Jest-DOM matchers setup for Vitest
│           ├── unit/
│           │   ├── smoke.test.tsx          [CREATED] Component smoke tests verifying heading & pillars
│           │   └── health.test.ts          [CREATED] Health API route contract verification
│           └── e2e/
│               ├── smoke.spec.ts           [CREATED] Playwright E2E title, h1, and API checks
│               └── a11y.spec.ts            [CREATED] Axe automated accessibility scan (WCAG 2.1 AA)
└── docs/
    └── PROGRESS_TRACKER.md                 [MODIFIED] Updated PKT-01 to PASS
```

---

## 4. Toolchain Versions

| Component | Pinned Version / Runtime | Verification Command |
| :--- | :--- | :--- |
| **Node.js** | `v24.13.0` | `node -v` |
| **npm** | `11.6.2` | `npm -v` |
| **Python** | `3.12.14` | `python --version` |
| **uv** | `0.12.17` | `uv --version` |
| **Docker** | `27.2.0` | `docker --version` |
| **Docker Compose** | `v2.29.2` | `docker compose version` |
| **Next.js** | `14.2.15` | `npm --workspace=apps/web list next` |
| **React** | `18.3.1` | `npm --workspace=apps/web list react` |
| **TypeScript** | `5.5.4` | `tsc --version` |
| **FastAPI** | `0.142.2` | `pip show fastapi` |
| **Uvicorn** | `0.54.0` | `pip show uvicorn` |
| **SQLAlchemy** | `2.1.3` | `pip show sqlalchemy` |
| **Asyncpg** | `0.31.0` | `pip show asyncpg` |
| **Pydantic** | `2.13.5` | `pip show pydantic` |
| **Ruff** | `0.16.10` | `ruff --version` |
| **Mypy** | `2.4.0` | `mypy --version` |
| **Pytest** | `9.1.1` | `pytest --version` |
| **Vitest** | `2.1.9` | `vitest --version` |
| **Playwright** | `1.57.0` | `npx playwright --version` |
| **Axe-core** | `4.10.0` | `npm list @axe-core/playwright` |
| **PostgreSQL Container**| `postgres:16-alpine` | `docker inspect sambal-db` |
| **MinIO Container** | `quay.io/minio/minio:latest` | `docker inspect sambal-s3` |

---

## 5. Architecture Boundaries Established

1. **ASR Provider Boundary:**
   - Interface `ASRProvider` in `backend/app/intelligence/contracts.py`.
   - `faster-whisper-turbo + CTranslate2 INT8` established as `BASELINE_CANDIDATE`.
   - Sub-second streaming claims deferred to hardware benchmarking in Packet 08.
2. **Canonical PostgreSQL Boundary:**
   - PostgreSQL 16+ is canonical across development integration, migrations, tests, E2E, CI, and production.
   - SQLite is prohibited as an architectural or release alternative; configuration validator raises immediate errors on non-PostgreSQL URIs.
3. **Emergency Adapter Boundary:**
   - Autonomous emergency dispatch by AI is prohibited.
   - `ERSS112Adapter` represents a human-authorized handoff boundary requiring operator sign-off.
4. **Reported Incident Urgency Boundary:**
   - Replaced statutory atrocity terminology with "Reported Incident Urgency".
   - The system extracts facts potentially relevant to urgency or routing; legal guilt is strictly an authorized human responsibility.
5. **Policy-Driven Follow-Up Boundary:**
   - Follow-up intervals are governed dynamically via `FollowUpPolicy` models rather than hardcoded 7/14-day rules.
6. **Provider Isolation Boundary:**
   - Domain logic imports only abstract protocols from `app.intelligence.contracts`.
   - Direct vendor SDK imports in application logic are prohibited.
7. **PII Protection Boundary:**
   - Regex-based filtering strips Aadhaar numbers, Indian telephone numbers, and email addresses prior to log persistence.

---

## 6. Execution Commands & Exact Results

### 6.1 Backend Quality Gates
```bash
# 1. Ruff Formatter Check
.venv\Scripts\ruff.exe format --check .
# Result: 18 files already formatted. Exit code: 0

# 2. Ruff Linter Check
.venv\Scripts\ruff.exe check .
# Result: All checks passed! Exit code: 0

# 3. Mypy Strict Type Check
.venv\Scripts\mypy.exe app
# Result: Success: no issues found in 12 source files. Exit code: 0

# 4. Pytest Suite
.venv\Scripts\pytest.exe -v
# Result: 13 passed in 0.08s. Exit code: 0

# 5. OpenAPI Schema Generation
python -c "from app.main import app; schema = app.openapi(); print('Paths:', len(schema['paths']))"
# Result: Paths: 4. Generation SUCCESS. Exit code: 0
```

### 6.2 Frontend Quality Gates
```bash
# 1. Prettier Code Style Check
npm run format:check
# Result: Checking formatting... All matched files use Prettier code style! Exit code: 0

# 2. Shared Contracts Build
npm --workspace=packages/contracts run build
# Result: tsc compiled cleanly. Exit code: 0

# 3. Strict TypeScript Compilation (Contracts + Web)
npm run typecheck
# Result: Zero type errors across packages/contracts and apps/web. Exit code: 0

# 4. Next.js ESLint
npm run lint
# Result: ✔ No ESLint warnings or errors. Exit code: 0

# 5. Vitest Unit & Component Smoke Tests
npm run test
# Result: 2 test files passed, 4 tests passed (health.test.ts, smoke.test.tsx). Exit code: 0

# 6. Next.js Production Build
npm run build
# Result: Compiled successfully, all 5 static pages prerendered. Exit code: 0

# 7. Playwright E2E Smoke & Axe Accessibility Tests
npm run test:e2e
# Result: 3 passed (4.5s)
#   - [chromium] homepage loads and displays correct metadata and headings: PASSED
#   - [chromium] health endpoint returns 200 OK with valid JSON structure: PASSED
#   - [chromium] homepage has zero WCAG 2.1 AA violations (Axe scan): PASSED
# Exit code: 0
```

### 6.3 Infrastructure Verification
```bash
# Docker Compose start
docker compose up -d db s3
# Result: Container sambal-db Started, Container sambal-s3 Started. Exit code: 0

# Live PostgreSQL Connectivity Verification
# Result: PostgreSQL Status: True, Latency: 82.63ms, Details: PostgreSQL connection operational

# Live MinIO S3 Connectivity Verification
# Result: S3 Status: True, Latency: 654.11ms, Details: S3 storage operational (sambal-ephemeral-audio)
```

---

## 7. Warnings & Dependency Audit Findings

- **ESLint & Next.js Notice:** `npm audit` flagged known advisories on Next.js 14 and development packages (`braces`, `glob`, `esbuild` via Vitest). Because the project is pinned to the stable Next.js 14 LTS baseline for App Router stability, these dependencies are monitored. A subsequent upgrade to Next.js 15/16 can be evaluated in Packet 27 (Security Hardening).
- **Docker Compose Obsolete Attribute:** Removed obsolete `version: '3.8'` attribute from `docker-compose.yml` to ensure clean compatibility with current Docker Compose v2.

---

## 8. External Dependencies

- **PostgreSQL 16 Alpine:** Canonical database instance provisioned via Docker on port `5493`.
- **MinIO Object Storage:** S3-compatible local object storage provisioned via Docker on port `9093`.
- **No External Cloud Calls:** All Packet 01 validation executed entirely locally in zero-cloud sandbox mode.

---

## 9. Known Limitations

- **No Domain Data Tables Yet:** In accordance with the Packet 01 boundary, database schema models, migrations, and tables are not yet created. They will be constructed in Packet 03.
- **Provisional SVI Baseline:** The SVI composite score formulas and weights are intentionally unencoded, marked as `PROVISIONAL_TRIAGE_POLICY`.
- **Sandbox Adapters:** Emergency and external support service adapters are defined as abstract protocols; live integration occurs in Packets 15 and 19.

---

## 10. Deliberately Not Implemented in Packet 01

To preserve architectural discipline, the following were intentionally excluded:
- Final relational database schema and tables (Packet 03).
- Authorization, RBAC, and Auth0/OIDC integration (Packet 04).
- Production UI intake screens and citizen chat interfaces (Packet 07).
- Speech-to-text inference pipeline and live WebSocket audio streaming (Packet 08).
- Multilingual NLP and distress keyword classifiers (Packet 09).
- Acoustic feature extraction and voice tremor analysis (Packet 10).
- SVI mathematical scoring and weighting (Packet 11).
- Operator copilot dashboard (Packet 13).
- External integrations (ERSS 112, Tele-MANAS, NALSA) (Packets 15, 19).

---

## 11. Next Packet

**Packet 02 — Product, Safety & Service Specification**
- Focus: Complete trauma-informed product specification, risk severity matrices, closed-loop referral state machine contracts, policy registers, and human-in-the-loop escalation criteria.

---

## 12. Git Commit SHA & Repository State

- **Branch:** `main`
- **Commit SHA:** `8352e24` (Full: `8352e24cedd96d4805d76b102149e310e1ce26a9`)
- **Repository State:** Clean working tree, all gates verified green.
