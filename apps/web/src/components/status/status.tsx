import type { ReactNode } from "react";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  CircleDashed,
  Clock3,
  FlaskConical,
  Radio,
  ShieldCheck,
  Wifi,
  WifiOff,
} from "lucide-react";
import { cn } from "@/lib/cn";

export type TruthStatus =
  | "NOT_STARTED"
  | "FOUNDATION_READY"
  | "BASELINE_CANDIDATE"
  | "PROVISIONAL"
  | "SANDBOX"
  | "ADAPTER_READY"
  | "LIVE"
  | "DEGRADED";

const statusMeta: Record<TruthStatus, { tone: string; icon: typeof Activity }> =
  {
    NOT_STARTED: { tone: "neutral", icon: Clock3 },
    FOUNDATION_READY: { tone: "success", icon: CheckCircle2 },
    BASELINE_CANDIDATE: { tone: "info", icon: CircleDashed },
    PROVISIONAL: { tone: "warning", icon: AlertTriangle },
    SANDBOX: { tone: "neutral", icon: FlaskConical },
    ADAPTER_READY: { tone: "info", icon: Radio },
    LIVE: { tone: "success", icon: Activity },
    DEGRADED: { tone: "warning", icon: AlertCircle },
  };

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={cn("badge", `badge--${tone}`)}>{children}</span>;
}

export function StatusBadge({ status }: { status: TruthStatus }) {
  const meta = statusMeta[status];
  const Icon = meta.icon;
  return (
    <Badge tone={meta.tone}>
      <Icon aria-hidden="true" />
      {status.replaceAll("_", " ")}
    </Badge>
  );
}

export type ConnectionState =
  "CONNECTED" | "RECONNECTING" | "OFFLINE" | "DEGRADED";

export function ConnectionStatus({ state }: { state: ConnectionState }) {
  const Icon =
    state === "CONNECTED" ? Wifi : state === "OFFLINE" ? WifiOff : Radio;
  const explanation = {
    CONNECTED: "Updates are available.",
    RECONNECTING:
      "Trying to restore updates. Your current work remains available.",
    OFFLINE: "Live updates are paused.",
    DEGRADED: "Some updates may arrive slowly.",
  }[state];
  return (
    <span
      className={cn("connection", `connection--${state.toLowerCase()}`)}
      role="status"
    >
      <Icon aria-hidden="true" />
      <span>
        <strong>{state}</strong>
        <small>{explanation}</small>
      </span>
    </span>
  );
}

export function HumanReviewStatus({
  state,
}: {
  state:
    | "AI SUGGESTION"
    | "AWAITING REVIEW"
    | "HUMAN CONFIRMED"
    | "HUMAN MODIFIED"
    | "DISMISSED"
    | "ESCALATED";
}) {
  const human = state.startsWith("HUMAN");
  return (
    <Badge
      tone={human ? "success" : state === "ESCALATED" ? "warning" : "info"}
    >
      {human ? (
        <ShieldCheck aria-hidden="true" />
      ) : (
        <CircleDashed aria-hidden="true" />
      )}
      {state}
    </Badge>
  );
}
