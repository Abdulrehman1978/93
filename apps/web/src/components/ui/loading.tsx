import type { HTMLAttributes } from "react";
import { LoaderCircle } from "lucide-react";
import { cn } from "@/lib/cn";
import { VisuallyHidden } from "@/components/accessibility";

export function Spinner({ label = "Loading" }: { label?: string }) {
  return (
    <span className="spinner" role="status">
      <LoaderCircle aria-hidden="true" />
      <VisuallyHidden>{label}</VisuallyHidden>
    </span>
  );
}

export function Progress({ value, label }: { value: number; label: string }) {
  const bounded = Math.max(0, Math.min(100, value));
  return (
    <div className="progress">
      <div className="progress__label">
        <span>{label}</span>
        <span>{bounded}%</span>
      </div>
      <progress max="100" value={bounded}>
        {bounded}%
      </progress>
    </div>
  );
}

export function Skeleton({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div aria-hidden="true" className={cn("skeleton", className)} {...props} />
  );
}
