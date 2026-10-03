import React from "react";
import {
  ShieldAlert,
  HeartPulse,
  Scale,
  CheckCircle2,
  Lock,
  Cpu,
  Server,
  Activity,
} from "lucide-react";
import type {
  ImmediateSafetyState,
  SVIBand,
  ReportedUrgencyLevel,
} from "@sambal/contracts";

interface ArchitecturePillar {
  title: string;
  badge: string;
  badgeColor: string;
  description: string;
  icon: React.ElementType;
  specs: string[];
}

export default function HomePage() {
  const sampleSafety: ImmediateSafetyState = "NO_IMMEDIATE_SIGNAL";
  const sampleSVIBand: SVIBand = "MODERATE";
  const sampleUrgency: ReportedUrgencyLevel = "PRIORITY";

  const pillars: ArchitecturePillar[] = [
    {
      title: "Immediate Safety Gate",
      badge: sampleSafety,
      badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
      description:
        "Zero-latency distress interrupt safeguarding citizens during active crisis. Escalations strictly require authorized human verification before emergency dispatch.",
      icon: ShieldAlert,
      specs: [
        "Acoustic tremor & distress keyword signals",
        "Human-in-the-loop ERSS 112 escalation boundary",
        "Automatic silent intake switch",
      ],
    },
    {
      title: "Stress & Vulnerability Index (SVI)",
      badge: `${sampleSVIBand} (Provisional)`,
      badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
      description:
        "Continuous 0–100 trauma-informed composite scoring calibrated across acoustic features, linguistic distress markers, and situational vulnerability.",
      icon: HeartPulse,
      specs: [
        "Provisional triage policy baseline (non-clinical)",
        "Multi-signal acoustic & transcript evidence",
        "Counterfactual explanation & human override",
      ],
    },
    {
      title: "Reported Incident Urgency",
      badge: sampleUrgency,
      badgeColor: "bg-blue-100 text-blue-800 border-blue-300",
      description:
        "Factual urgency classification based on reported narrative elements. The system does not determine legal guilt, offence proof, or complainant veracity.",
      icon: Scale,
      specs: [
        "Facts-informed routing for statutory officers",
        "Policy-driven follow-up scheduling",
        "Full audit trail and evidentiary provenance",
      ],
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section
        className="bg-white rounded-xl p-8 border border-slate-200/80 shadow-sm"
        aria-labelledby="foundation-heading"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-teal-50 text-teal-800 border border-teal-200">
              <span className="w-2 h-2 rounded-full bg-teal-600"></span>
              Packet 01 — Repository Foundation & Toolchain
            </div>
            <h1
              id="foundation-heading"
              className="text-2xl md:text-3xl font-bold text-civic-dark tracking-tight"
            >
              SAMBAL Real-Time Multilingual Trauma-Aware Intelligence & Response
              Layer
            </h1>
            <p className="text-slate-600 text-sm max-w-3xl leading-relaxed">
              SIH26093 Problem Statement for the National Helpline Against
              Atrocities (14566) and Integrated Portal, under the Ministry of
              Social Justice & Empowerment. Operating on the V3 Lean-Core
              Architecture.
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
              href="http://localhost:8093/health/live"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center px-4 py-2 text-xs font-medium rounded-lg text-white bg-civic-teal hover:bg-civic-sage transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-civic-teal focus:outline-none"
            >
              <Server className="w-3.5 h-3.5 mr-1.5" />
              FastAPI Liveness
            </a>
          </div>
        </div>
      </section>

      {/* 3-Dimensional Risk Architecture */}
      <section aria-labelledby="pillars-heading">
        <div className="mb-4">
          <h2
            id="pillars-heading"
            className="text-lg font-bold text-civic-dark tracking-tight"
          >
            Three-Dimensional Triage & Assessment Architecture
          </h2>
          <p className="text-xs text-slate-500">
            Authoritative assessment model preserving evidence provenance and
            human review boundaries.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {pillars.map((pillar) => {
            const Icon = pillar.icon;
            return (
              <div
                key={pillar.title}
                className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center text-civic-teal">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span
                      className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${pillar.badgeColor}`}
                    >
                      {pillar.badge}
                    </span>
                  </div>
                  <h3 className="text-base font-semibold text-slate-900 mb-2">
                    {pillar.title}
                  </h3>
                  <p className="text-xs text-slate-600 mb-4 leading-relaxed">
                    {pillar.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <h4 className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-2">
                    Architectural Guardrails
                  </h4>
                  <ul className="space-y-1.5">
                    {pillar.specs.map((spec, i) => (
                      <li
                        key={i}
                        className="text-xs text-slate-700 flex items-start"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 text-civic-teal mr-1.5 mt-0.5 flex-shrink-0" />
                        <span>{spec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* V3 Lean-Core Stack Status */}
      <section
        className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm"
        aria-labelledby="stack-heading"
      >
        <h2
          id="stack-heading"
          className="text-base font-bold text-civic-dark mb-4"
        >
          V3 Lean-Core Toolchain & Architectural Boundary Status
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-slate-900 font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                <Server className="w-4 h-4 text-civic-teal" />
                FastAPI Monolith
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                Active
              </span>
            </div>
            <p className="text-slate-500">
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
            <p className="text-slate-500">
              PostgreSQL 16 canonical across all environments. Zero SQLite
              reliance.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-slate-900 font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-civic-teal" />
                ASR Status
              </span>
              <span className="text-[10px] bg-sky-100 text-sky-800 px-1.5 py-0.5 rounded">
                Candidate
              </span>
            </div>
            <p className="text-slate-500">
              faster-whisper-turbo is BASELINE_CANDIDATE. Subject to Packet 08
              benchmark.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-slate-900 font-semibold mb-1">
              <span className="flex items-center gap-1.5">
                <Lock className="w-4 h-4 text-civic-teal" />
                PII-Safe Logging
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                Enforced
              </span>
            </div>
            <p className="text-slate-500">
              Zero-leakage regex redaction for Aadhaar, phones, emails in all
              logs.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

function Database(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5V19A9 3 0 0 0 21 19V5" />
      <path d="M3 12A9 3 0 0 0 21 12" />
    </svg>
  );
}
