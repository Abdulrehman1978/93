import React from "react";
import {
  Activity,
  Server,
  Shield,
  Database,
  Cpu,
  Lock,
  CheckCircle2,
  Clock,
  AlertTriangle,
} from "lucide-react";

interface ComponentCapability {
  name: string;
  category: string;
  status:
    | "FOUNDATION_READY"
    | "BASELINE_CANDIDATE"
    | "PROVISIONAL"
    | "SANDBOX"
    | "NOT_STARTED";
  description: string;
  notes: string;
}

export default function HomePage() {
  const capabilities: ComponentCapability[] = [
    {
      name: "Monorepo Toolchain & App Shells",
      category: "Platform Core",
      status: "FOUNDATION_READY",
      description:
        "Next.js 16 Active-LTS PWA shell, FastAPI Modular Monolith, shared contracts, and Docker dev environment.",
      notes: "Clean-CI verified across unit, E2E, and Axe a11y test suites.",
    },
    {
      name: "Canonical PostgreSQL Engine",
      category: "Data Persistence",
      status: "FOUNDATION_READY",
      description:
        "PostgreSQL 16 connection pool with asyncpg driver and strict rejection of non-PostgreSQL / SQLite URIs.",
      notes:
        "Authoritative database across dev, CI, integration, and production.",
    },
    {
      name: "S3 Object Storage & Bucket Readiness",
      category: "Object Storage",
      status: "FOUNDATION_READY",
      description:
        "MinIO/S3 connection with deterministic bucket readiness verification via non-blocking threadpool I/O.",
      notes: "Local MinIO on port 9093; bucket initialization verified.",
    },
    {
      name: "Baseline PII-Safe Logging Filter",
      category: "Privacy & Security",
      status: "FOUNDATION_READY",
      description:
        "Regex-based redaction for Aadhaar numbers, Indian mobile phones, and emails with structured key filtering.",
      notes:
        "Baseline filter; not a complete zero-leakage guarantee. Prohibited domain fields filtered.",
    },
    {
      name: "Speech-to-Text Pipeline (ASR)",
      category: "Speech Intelligence",
      status: "BASELINE_CANDIDATE",
      description:
        "faster-whisper-turbo + CTranslate2 INT8 designated as initial local baseline candidate.",
      notes:
        "Requires Packet 08 benchmarking against IndicConformer/Bhashini across 11 explicit metrics.",
    },
    {
      name: "Stress & Vulnerability Index (SVI)",
      category: "Triage Assessment",
      status: "PROVISIONAL",
      description:
        "Trauma-informed 0-100 composite framework. No final mathematical formula encoded in foundation.",
      notes:
        "Marked PROVISIONAL_TRIAGE_POLICY. Final parameterization belongs to Packet 11.",
    },
    {
      name: "Emergency Response (ERSS 112)",
      category: "External Adapters",
      status: "SANDBOX",
      description:
        "Human-authorized emergency handoff boundary. Autonomous dispatch is strictly prohibited.",
      notes:
        "All escalations require human operator verification and authorization.",
    },
    {
      name: "Citizen Intake & Operator Copilot",
      category: "Interaction Surfaces",
      status: "NOT_STARTED",
      description:
        "Multimodal citizen intake (speak/write/silent) and supervisor triage dashboard.",
      notes: "Scheduled for implementation in Packets 07 and 13.",
    },
  ];

  const getStatusBadge = (status: ComponentCapability["status"]) => {
    switch (status) {
      case "FOUNDATION_READY":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
            FOUNDATION_READY
          </span>
        );
      case "BASELINE_CANDIDATE":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-sky-100 text-sky-800 border border-sky-300">
            <Cpu className="w-3 h-3 mr-1 text-sky-600" />
            BASELINE_CANDIDATE
          </span>
        );
      case "PROVISIONAL":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-100 text-amber-800 border border-amber-300">
            <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" />
            PROVISIONAL
          </span>
        );
      case "SANDBOX":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-purple-100 text-purple-800 border border-purple-300">
            <Shield className="w-3 h-3 mr-1 text-purple-600" />
            SANDBOX
          </span>
        );
      case "NOT_STARTED":
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-300">
            <Clock className="w-3 h-3 mr-1 text-slate-500" />
            NOT_STARTED
          </span>
        );
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <section
        className="bg-white rounded-xl p-8 border border-slate-200/80 shadow-sm"
        aria-labelledby="foundation-heading"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-teal-50 text-teal-800 border border-teal-200">
              <span className="w-2 h-2 rounded-full bg-teal-600"></span>
              Packet 01R — Repository Foundation Remediation
            </div>
            <h1
              id="foundation-heading"
              className="text-2xl md:text-3xl font-bold text-civic-dark tracking-tight"
            >
              SAMBAL Intelligence & Response Layer — Architecture & Foundation
              Status
            </h1>
            <p className="text-slate-600 text-sm max-w-3xl leading-relaxed">
              SIH26093 Problem Statement for the National Helpline Against
              Atrocities (14566) and Integrated Portal. Operating under the V3
              Lean-Core Architecture. Substantive domain capabilities are
              tracked with truthful capability states.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <a
              id="view-health-btn"
              href="/api/health"
              className="inline-flex items-center justify-center px-4 py-2 text-xs font-medium rounded-lg text-civic-dark bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors focus:ring-2 focus:ring-civic-teal focus:outline-none"
            >
              <Activity className="w-3.5 h-3.5 mr-1.5 text-civic-teal" />
              Web Health API
            </a>
            <a
              id="view-backend-health-btn"
              href="/api/backend/health/live"
              className="inline-flex items-center justify-center px-4 py-2 text-xs font-medium rounded-lg text-white bg-civic-teal hover:bg-civic-sage transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-civic-teal focus:outline-none"
            >
              <Server className="w-3.5 h-3.5 mr-1.5" />
              Backend Liveness
            </a>
          </div>
        </div>
      </section>

      {/* Capability & Architecture State Matrix */}
      <section
        aria-labelledby="capabilities-heading"
        className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm"
      >
        <div className="mb-6">
          <h2
            id="capabilities-heading"
            className="text-lg font-bold text-civic-dark tracking-tight"
          >
            Component Capability & Truth-State Matrix
          </h2>
          <p className="text-xs text-slate-600">
            Authoritative tracking of foundation deliverables, provisional
            policies, candidate models, and pending domains.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {capabilities.map((cap) => (
            <div
              key={cap.name}
              className="p-5 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    {cap.category}
                  </span>
                  {getStatusBadge(cap.status)}
                </div>
                <h3 className="text-sm font-bold text-slate-900 mb-1">
                  {cap.name}
                </h3>
                <p className="text-xs text-slate-600 mb-3 leading-relaxed">
                  {cap.description}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-200/60 text-[11px] text-slate-600 flex items-start">
                <span className="font-semibold text-slate-700 mr-1.5 flex-shrink-0">
                  Engineering Note:
                </span>
                <span>{cap.notes}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* V3 Lean-Core Infrastructure Boundaries */}
      <section
        className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm"
        aria-labelledby="boundaries-heading"
      >
        <h2
          id="boundaries-heading"
          className="text-base font-bold text-civic-dark mb-4"
        >
          V3 Lean-Core Verified Infrastructure Boundaries
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-slate-900 font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                <Server className="w-4 h-4 text-civic-teal" />
                FastAPI Monolith
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                Port 8093
              </span>
            </div>
            <p className="text-slate-600">
              Python 3.12, strict typing, RFC 7807 problem details, correlation
              IDs.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-slate-900 font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                <Database className="w-4 h-4 text-civic-teal" />
                Canonical PostgreSQL
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                Port 5493
              </span>
            </div>
            <p className="text-slate-600">
              PostgreSQL 16 canonical across all environments. Zero SQLite
              reliance.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-slate-900 font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-civic-teal" />
                Object Storage
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                Port 9093
              </span>
            </div>
            <p className="text-slate-600">
              MinIO S3 storage with threadpool-isolated bucket readiness
              checking.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-slate-900 font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                <Lock className="w-4 h-4 text-civic-teal" />
                PII Redaction Filter
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                Active
              </span>
            </div>
            <p className="text-slate-600">
              Baseline regex sanitization for Aadhaar, phones, emails in logs.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
