"use client";

import { LogOut } from "lucide-react";
import { useEffect } from "react";
import { Button } from "@/components/ui";

const configuredQuickExitUrl = process.env.NEXT_PUBLIC_QUICK_EXIT_URL;
const deploymentEnvironment = process.env.NEXT_PUBLIC_APP_ENV;

if (
  (deploymentEnvironment === "production" ||
    deploymentEnvironment === "staging") &&
  !configuredQuickExitUrl
) {
  throw new Error(
    "NEXT_PUBLIC_QUICK_EXIT_URL must be configured for production and staging deployments.",
  );
}

const QUICK_EXIT_URL = configuredQuickExitUrl || "/";

export function clearCitizenSession() {
  if (typeof window === "undefined") return;
  window.sessionStorage.clear();
}

export function QuickExit() {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      clearCitizenSession();
      window.location.replace(QUICK_EXIT_URL);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const exit = () => {
    clearCitizenSession();
    window.location.replace(QUICK_EXIT_URL);
  };

  return (
    <Button
      type="button"
      variant="danger"
      size="md"
      className="quick-exit"
      onClick={exit}
      onKeyDown={(event) => {
        if (event.key === "Escape") exit();
      }}
    >
      <LogOut aria-hidden="true" /> Quick Exit
    </Button>
  );
}
