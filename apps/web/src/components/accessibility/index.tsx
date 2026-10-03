"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/cn";

export function SkipLink({ href = "#main-content" }: { href?: string }) {
  return (
    <a className="skip-link" href={href}>
      Skip to main content
    </a>
  );
}

export function VisuallyHidden({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <span className={cn("visually-hidden", className)}>{children}</span>;
}

export function LiveRegion({
  children,
  assertive = false,
  ...props
}: HTMLAttributes<HTMLDivElement> & { assertive?: boolean }) {
  return (
    <div
      aria-atomic="true"
      aria-live={assertive ? "assertive" : "polite"}
      role={assertive ? "alert" : "status"}
      {...props}
    >
      {children}
    </div>
  );
}
