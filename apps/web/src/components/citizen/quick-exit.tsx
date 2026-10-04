"use client";

import { LogOut } from "lucide-react";
import { useEffect } from "react";
import { Button } from "@/components/ui";

const QUICK_EXIT_URL = process.env.NEXT_PUBLIC_QUICK_EXIT_URL || "/";

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
