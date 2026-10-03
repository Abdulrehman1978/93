import type { ReactNode } from "react";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Info,
  RefreshCw,
  WifiOff,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { Button, LinkButton } from "./button";

export type FeedbackTone = "info" | "success" | "warning" | "danger";

const icons = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: AlertCircle,
};

export function Alert({
  title,
  children,
  tone = "info",
  className,
}: {
  title: string;
  children: ReactNode;
  tone?: FeedbackTone;
  className?: string;
}) {
  const Icon = icons[tone];
  return (
    <div
      className={cn("alert", `alert--${tone}`, className)}
      role={tone === "danger" ? "alert" : "status"}
    >
      <Icon aria-hidden="true" className="alert__icon" />
      <div>
        <strong className="alert__title">{title}</strong>
        <div className="alert__body">{children}</div>
      </div>
    </div>
  );
}

export function InlineNotice(props: Parameters<typeof Alert>[0]) {
  return <Alert {...props} className={cn("alert--inline", props.className)} />;
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="state-panel">
      <Info aria-hidden="true" />
      <h3>{title}</h3>
      <p>{description}</p>
      {action ? <div className="state-panel__actions">{action}</div> : null}
    </div>
  );
}

export function ErrorState({
  title = "This information could not be loaded",
  description,
  referenceId,
  onRetry,
  safeHref = "/",
}: {
  title?: string;
  description: string;
  referenceId?: string;
  onRetry?: () => void;
  safeHref?: string;
}) {
  return (
    <div className="state-panel state-panel--error" role="alert">
      <AlertCircle aria-hidden="true" />
      <h3>{title}</h3>
      <p>{description}</p>
      {referenceId ? (
        <p className="state-panel__reference">Reference ID: {referenceId}</p>
      ) : null}
      <div className="state-panel__actions">
        {onRetry ? (
          <Button variant="secondary" onClick={onRetry}>
            <RefreshCw aria-hidden="true" /> Retry
          </Button>
        ) : null}
        <LinkButton href={safeHref} variant="quiet">
          Return to overview
        </LinkButton>
      </div>
    </div>
  );
}

export function DegradedNotice({ children }: { children?: ReactNode }) {
  return (
    <Alert title="Some automated support is unavailable" tone="warning">
      <p>
        {children ??
          "You can continue recording the complaint and complete human review. Saved information is not affected."}
      </p>
    </Alert>
  );
}

export function OfflineState() {
  return (
    <div className="state-panel">
      <WifiOff aria-hidden="true" />
      <h3>Connection unavailable</h3>
      <p>
        Keep this page open. Reconnection can continue without losing this
        synthetic example.
      </p>
    </div>
  );
}
