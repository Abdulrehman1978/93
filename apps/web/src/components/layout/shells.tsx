"use client";

import type { ReactNode } from "react";
import { Accessibility, CircleHelp } from "lucide-react";
import { SkipLink } from "@/components/accessibility";
import { LanguageSelector } from "@/components/language-selector";
import { StatusBadge } from "@/components/status";
import { cn } from "@/lib/cn";
import { QuickExit } from "@/components/citizen/quick-exit";
import { useEffect, useState } from "react";

function PrototypeIdentity() {
  return (
    <a className="product-identity" href="/" aria-label="SAMBAL prototype home">
      <span aria-hidden="true" className="product-identity__mark">
        S
      </span>
      <span>
        <strong>SAMBAL</strong>
        <small>SIH integration prototype</small>
      </span>
    </a>
  );
}

function FoundationFooter() {
  return (
    <footer className="site-footer">
      <div>
        <strong>SAMBAL / NHAA integration prototype</strong>
        <p>No official government emblem or endorsement is represented.</p>
      </div>
      <nav aria-label="Footer information">
        <span>Privacy notice shown before intake</span>
        <span>Accessibility baseline available</span>
        <span>Citizen intake available</span>
        <span>Service status foundation ready</span>
      </nav>
    </footer>
  );
}

export function PublicShell({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("app-shell app-shell--public", className)}>
      <SkipLink />
      <header className="site-header">
        <PrototypeIdentity />
        <nav aria-label="Utility navigation" className="site-header__actions">
          <a href="/design-system#language-rtl">
            <span>
              <CircleHelp aria-hidden="true" /> Language
            </span>
          </a>
          <a href="/design-system#accessibility">
            <span>
              <Accessibility aria-hidden="true" /> Accessibility
            </span>
          </a>
        </nav>
      </header>
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
      <FoundationFooter />
    </div>
  );
}

export function CitizenShell({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState("en");
  const [sessionActive, setSessionActive] = useState(false);

  useEffect(() => {
    const sync = () => {
      const stored = window.sessionStorage.getItem("sambal:intake:language");
      if (stored) setLanguage(stored);
      setSessionActive(
        Boolean(window.sessionStorage.getItem("sambal:intake:session")),
      );
    };
    sync();
    window.addEventListener("sambal:session-started", sync);
    window.addEventListener("sambal:session-ended", sync);
    return () => {
      window.removeEventListener("sambal:session-started", sync);
      window.removeEventListener("sambal:session-ended", sync);
    };
  }, []);

  return (
    <PublicShell className="app-shell--citizen">
      <div className="citizen-toolbar" aria-label="Citizen safety controls">
        <LanguageSelector
          languages={[
            { code: "en", nativeName: "English", englishName: "English" },
            { code: "hi", nativeName: "हिन्दी", englishName: "Hindi" },
            { code: "mr", nativeName: "मराठी", englishName: "Marathi" },
          ]}
          defaultCode={language}
          disabled={sessionActive}
          onChange={(code) => {
            window.sessionStorage.setItem("sambal:intake:language", code);
          }}
        />
        {sessionActive ? (
          <span className="citizen-language-lock" role="status">
            Language locked for this private session; start a new session to
            change it.
          </span>
        ) : null}
        <QuickExit />
      </div>
      <div className="citizen-content">{children}</div>
    </PublicShell>
  );
}

export function OperatorShell({
  children,
  aside,
}: {
  children: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <div className="app-shell app-shell--operator">
      <SkipLink />
      <header className="operator-bar">
        <PrototypeIdentity />
        <StatusBadge status="FOUNDATION_READY" />
      </header>
      <nav className="operator-nav" aria-label="Operator foundation navigation">
        <span aria-current="page">Workspace foundation</span>
        <span>Navigation arrives with operator workflows</span>
      </nav>
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
      {aside ? <aside aria-label="Context panel">{aside}</aside> : null}
    </div>
  );
}

export function InstitutionalShell({ children }: { children: ReactNode }) {
  return (
    <PublicShell className="app-shell--institutional">{children}</PublicShell>
  );
}
