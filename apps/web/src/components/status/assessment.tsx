import type { ReactNode } from "react";
import {
  AlertCircle,
  AlertTriangle,
  CircleDashed,
  Flag,
  HeartPulse,
  ShieldAlert,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { Badge } from "./status";

type ImmediateSafetyState =
  | "NO_IMMEDIATE_SIGNAL"
  | "REVIEW_RECOMMENDED"
  | "ELEVATED"
  | "CRITICAL_REVIEW"
  | "INSUFFICIENT_INFORMATION";
type SviState = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
type UrgencyState = "ROUTINE" | "PRIORITY" | "URGENT" | "CRITICAL";
export type UncertaintyState =
  | "INSUFFICIENT_EVIDENCE"
  | "LOW_AUDIO_QUALITY"
  | "TRANSCRIPT_UNCERTAIN"
  | "LANGUAGE_UNCERTAIN"
  | "MODEL_DISAGREEMENT"
  | "OUT_OF_DISTRIBUTION"
  | "HUMAN_REVIEW_REQUIRED";

function AssessmentState({
  dimension,
  state,
  explanation,
  tone,
  icon,
}: {
  dimension: string;
  state: string;
  explanation: string;
  tone: string;
  icon: ReactNode;
}) {
  return (
    <article className={cn("assessment-state", `assessment-state--${tone}`)}>
      <div className="assessment-state__symbol" aria-hidden="true">
        {icon}
      </div>
      <div>
        <p className="assessment-state__dimension">{dimension}</p>
        <h3>{state.replaceAll("_", " ")}</h3>
        <p>{explanation}</p>
      </div>
    </article>
  );
}

export function ImmediateSafety({
  state,
  explanation,
}: {
  state: ImmediateSafetyState;
  explanation?: string;
}) {
  const tone =
    state === "CRITICAL_REVIEW"
      ? "critical"
      : state === "ELEVATED"
        ? "high"
        : state === "REVIEW_RECOMMENDED"
          ? "moderate"
          : "neutral";
  return (
    <AssessmentState
      dimension="Immediate safety signal"
      state={state}
      tone={tone}
      icon={<ShieldAlert />}
      explanation={
        explanation ??
        (state === "NO_IMMEDIATE_SIGNAL"
          ? "No immediate signal was identified in the available information. This does not mean the person is safe."
          : "This state recommends proportionate human attention based on the available information.")
      }
    />
  );
}

export function SviStateCard({ state }: { state: SviState }) {
  const tone = {
    LOW: "low",
    MODERATE: "moderate",
    HIGH: "high",
    CRITICAL: "critical",
  }[state];
  return (
    <AssessmentState
      dimension="Stress vulnerability — provisional triage"
      state={state}
      tone={tone}
      icon={<HeartPulse />}
      explanation="A qualitative triage band for human review. It is not a diagnosis, credibility judgment, or measure of case importance."
    />
  );
}

export function IncidentUrgency({ state }: { state: UrgencyState }) {
  const tone = {
    ROUTINE: "neutral",
    PRIORITY: "moderate",
    URGENT: "high",
    CRITICAL: "critical",
  }[state];
  return (
    <AssessmentState
      dimension="Reported incident urgency"
      state={state}
      tone={tone}
      icon={<Flag />}
      explanation="Urgency of the reported circumstances for authorized human review, independent of emotional presentation."
    />
  );
}

export function Uncertainty({ state }: { state: UncertaintyState }) {
  return (
    <div className="uncertainty" role="status">
      <CircleDashed aria-hidden="true" />
      <div>
        <strong>{state.replaceAll("_", " ")}</strong>
        <p>
          Uncertainty is expected system information. A human reviewer should
          verify before relying on this output.
        </p>
      </div>
    </div>
  );
}

export function EvidenceChip({
  signal,
  modality,
  source,
  confidence,
  quality,
  reviewed = false,
}: {
  signal: string;
  modality: string;
  source: string;
  confidence: "High" | "Moderate" | "Low";
  quality: string;
  reviewed?: boolean;
}) {
  return (
    <div className="evidence-chip">
      <AlertCircle aria-hidden="true" />
      <div>
        <strong>{signal}</strong>
        <span>
          {modality} · {source}
        </span>
        <span>
          {confidence} confidence · {quality}
        </span>
      </div>
      <Badge tone={reviewed ? "success" : "warning"}>
        {reviewed ? "HUMAN REVIEWED" : "REVIEW PENDING"}
      </Badge>
    </div>
  );
}

export type Provenance =
  | "COMPLAINANT_REPORTED"
  | "SUPPORT_PERSON_REPORTED"
  | "OFFICER_REPORTED"
  | "AI_EXTRACTED"
  | "AI_ESTIMATED"
  | "HUMAN_CONFIRMED"
  | "OFFICIAL_SOURCE"
  | "SERVICE_PROVIDER_REPORTED"
  | "SYNTHETIC_DEMO"
  | "NEEDS_VERIFICATION";

export function ProvenanceChip({ value }: { value: Provenance }) {
  const tone =
    value === "HUMAN_CONFIRMED" || value === "OFFICIAL_SOURCE"
      ? "success"
      : value.startsWith("AI_")
        ? "info"
        : value === "NEEDS_VERIFICATION"
          ? "warning"
          : "neutral";
  const Icon =
    value === "NEEDS_VERIFICATION"
      ? AlertTriangle
      : value.startsWith("AI_")
        ? CircleDashed
        : AlertCircle;
  return (
    <Badge tone={tone}>
      <Icon aria-hidden="true" /> {value.replaceAll("_", " ")}
    </Badge>
  );
}
