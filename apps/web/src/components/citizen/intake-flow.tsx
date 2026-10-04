"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Check, Copy, ShieldCheck } from "lucide-react";
import {
  Button,
  Card,
  CardContent,
  FieldError,
  FormField,
  Input,
  LinkButton,
  Textarea,
} from "@/components/ui";

type FlowMode = "help" | "write" | "silent" | "speak" | "received";
type IntakeMode = "TEXT" | "SILENT" | "VOICE";

type SessionInfo = {
  session_id: string;
  session_token: string;
  expires_at: string;
  policy_version: string;
  available_modes: IntakeMode[];
  channel?: "WEB";
  interaction_mode?: IntakeMode | "UNSELECTED";
  status?: string;
  language?: string | null;
  intake_ready?: boolean;
};

type Policy = {
  policy_version: string;
  served_locale: string;
  translation_status: string;
  required_notices: Array<{
    purpose_code: string;
    name: string;
    why_needed: string;
    data_categories: string[];
    recipients: string[];
    retention_status: string;
    effect_of_decline: string;
  }>;
  intake_ready: boolean;
};

type Receipt = {
  tracking_reference: string;
  received_at: string;
  interaction_mode: IntakeMode;
  entry_count: number;
  case_created: boolean;
};

type WriteDraft = {
  narrative: string;
  optional_when: string;
  optional_location: string;
  optional_current_safety: string;
  optional_contact_preference: string;
  optional_contact_value: string;
};

const API = "/api/backend/api/v1";
const SESSION_KEY = "sambal:intake:session";
const DRAFT_KEY = "sambal:intake:draft";
const RECEIPT_KEY = "sambal:intake:receipt";
const LANGUAGE_KEY = "sambal:intake:language";
const WRITE_SUBMISSION_KEY = "sambal:intake:write-submission";
const SILENT_SUBMISSION_KEY = "sambal:intake:silent-submission";

const emptyDraft: WriteDraft = {
  narrative: "",
  optional_when: "",
  optional_location: "",
  optional_current_safety: "",
  optional_contact_preference: "",
  optional_contact_value: "",
};

class RequestError extends Error {
  status: number;
  type?: string;

  constructor(message: string, status: number, type?: string) {
    super(message);
    this.name = "RequestError";
    this.status = status;
    this.type = type;
  }
}

function clientId(prefix: string) {
  const random =
    globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);
  return `${prefix}-${random}`.slice(0, 80);
}

async function requestJson<T>(
  path: string,
  init: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  headers.set("Cache-Control", "no-store");
  if (init.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("X-Channel-Session-Token", token);
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      detail?: string | { message?: string };
      type?: string;
    } | null;
    const detail =
      typeof body?.detail === "string"
        ? body.detail
        : body?.detail?.message ||
          "We could not complete that step. Please try again.";
    throw new RequestError(detail, response.status, body?.type);
  }
  return (await response.json()) as T;
}

function loadSession(): SessionInfo | null {
  try {
    const raw = window.sessionStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as SessionInfo) : null;
  } catch {
    return null;
  }
}

function saveSession(session: SessionInfo) {
  window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function Notice({ policy }: { policy: Policy | null }) {
  if (!policy) return null;
  return (
    <section className="citizen-notice" aria-labelledby="notice-heading">
      <p className="eyebrow">Before you continue</p>
      <h2 id="notice-heading">What will happen with what you share</h2>
      <p className="citizen-notice__truth">
        Language served: {policy.served_locale}. Translation status:{" "}
        {policy.translation_status}.
      </p>
      {policy.required_notices.map((notice) => (
        <div className="citizen-notice__item" key={notice.purpose_code}>
          <h3>{notice.name}</h3>
          <p>{notice.why_needed}</p>
          <dl>
            <div>
              <dt>Information</dt>
              <dd>{notice.data_categories.join(", ")}</dd>
            </div>
            <div>
              <dt>Recipients</dt>
              <dd>{notice.recipients.join(", ")}</dd>
            </div>
            <div>
              <dt>Retention</dt>
              <dd>{notice.retention_status}</dd>
            </div>
          </dl>
        </div>
      ))}
      <p className="citizen-notice__alternative">
        You can use Write, Speak, or Silent intake. No microphone is used unless
        a future version clearly tells you it is active.
      </p>
    </section>
  );
}

function ChoiceButton({
  value,
  label,
  description,
  selected,
  onClick,
}: {
  value: string;
  label: string;
  description?: string;
  selected: string;
  onClick: (value: string) => void;
}) {
  return (
    <button
      type="button"
      className={`citizen-choice ${selected === value ? "is-selected" : ""}`}
      aria-pressed={selected === value}
      onClick={() => onClick(value)}
    >
      <span className="citizen-choice__radio" aria-hidden="true">
        {selected === value ? <Check /> : null}
      </span>
      <span>
        <strong>{label}</strong>
        {description ? <small>{description}</small> : null}
      </span>
    </button>
  );
}

export function CitizenIntakeFlow({ mode }: { mode: FlowMode }) {
  const router = useRouter();
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [continued, setContinued] = useState(false);
  const [writeStep, setWriteStep] = useState<"form" | "review">("form");
  const [draft, setDraft] = useState<WriteDraft>(emptyDraft);
  const [silentStep, setSilentStep] = useState(0);
  const [silent, setSilent] = useState({
    current_safety: "",
    urgent_help: "",
    contact_preference: "",
    optional_contact_value: "",
  });
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [submissionIds, setSubmissionIds] = useState({ write: "", silent: "" });
  const [hydrating, setHydrating] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);

  useEffect(() => {
    const storedSession = loadSession();
    setSession(storedSession);
    try {
      const storedDraft = window.sessionStorage.getItem(DRAFT_KEY);
      if (storedDraft)
        setDraft({
          ...emptyDraft,
          ...(JSON.parse(storedDraft) as Partial<WriteDraft>),
        });
      const storedReceipt = window.sessionStorage.getItem(RECEIPT_KEY);
      if (storedReceipt) setReceipt(JSON.parse(storedReceipt) as Receipt);
      setSubmissionIds({
        write:
          window.sessionStorage.getItem(WRITE_SUBMISSION_KEY) ||
          clientId("write"),
        silent:
          window.sessionStorage.getItem(SILENT_SUBMISSION_KEY) ||
          clientId("silent"),
      });
    } catch {
      // A missing draft is safe; the user can continue without it.
    }
    if (!storedSession) {
      setHydrating(false);
      return;
    }
    void (async () => {
      try {
        const state = await requestJson<SessionInfo>(
          `/channel/sessions/${storedSession.session_id}`,
          {},
          storedSession.session_token,
        );
        const restored = { ...storedSession, ...state };
        setSession(restored);
        saveSession(restored);
        const restoredPolicy = await requestJson<Policy>(
          `/channel/sessions/${storedSession.session_id}/policy`,
          {},
          storedSession.session_token,
        );
        setPolicy(restoredPolicy);
        setContinued(
          Boolean(state.intake_ready || restoredPolicy.intake_ready),
        );
      } catch (cause) {
        if (
          cause instanceof RequestError &&
          [401, 403].includes(cause.status)
        ) {
          window.sessionStorage.removeItem(SESSION_KEY);
          window.sessionStorage.removeItem(WRITE_SUBMISSION_KEY);
          window.sessionStorage.removeItem(SILENT_SUBMISSION_KEY);
          setSession(null);
          setSessionExpired(true);
        } else {
          setError(
            cause instanceof Error
              ? cause.message
              : "We could not restore this private session.",
          );
        }
      } finally {
        setHydrating(false);
      }
    })();
  }, []);

  useEffect(() => {
    const heading = document.querySelector<HTMLElement>("#main-content h1");
    heading?.focus({ preventScroll: true });
  }, [mode, writeStep, silentStep, continued, sessionExpired]);

  useEffect(() => {
    document.title =
      mode === "silent"
        ? "Citizen Information Services"
        : "SAMBAL — Civic service prototype";
  }, [mode]);

  useEffect(() => {
    if (mode !== "write") return;
    window.sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  }, [draft, mode]);

  useEffect(() => {
    if (!submissionIds.write || !submissionIds.silent) return;
    window.sessionStorage.setItem(WRITE_SUBMISSION_KEY, submissionIds.write);
    window.sessionStorage.setItem(SILENT_SUBMISSION_KEY, submissionIds.silent);
  }, [submissionIds]);

  const updateDraft = (key: keyof WriteDraft, value: string) =>
    setDraft((current) => ({ ...current, [key]: value }));
  const hasSession = Boolean(session?.session_id && session.session_token);

  useEffect(() => {
    if (hydrating || mode === "help" || mode === "received" || !session) return;
    const expected: Record<
      Exclude<FlowMode, "help" | "received">,
      IntakeMode
    > = {
      write: "TEXT",
      silent: "SILENT",
      speak: "VOICE",
    };
    if (
      !session.intake_ready ||
      (session.interaction_mode &&
        session.interaction_mode !== "UNSELECTED" &&
        session.interaction_mode !== expected[mode])
    ) {
      router.replace("/help");
    }
  }, [hydrating, mode, router, session]);

  const begin = async () => {
    setBusy(true);
    setError("");
    try {
      window.sessionStorage.removeItem(SESSION_KEY);
      window.sessionStorage.removeItem(WRITE_SUBMISSION_KEY);
      window.sessionStorage.removeItem(SILENT_SUBMISSION_KEY);
      setPolicy(null);
      setContinued(false);
      const locale = window.sessionStorage.getItem(LANGUAGE_KEY) || "en";
      const created = await requestJson<SessionInfo>("/channel/sessions", {
        method: "POST",
        body: JSON.stringify({
          channel: "WEB",
          interaction_mode: "UNSELECTED",
          locale,
          client_request_id: clientId("web"),
        }),
      });
      saveSession(created);
      setSession(created);
      setSessionExpired(false);
      window.dispatchEvent(new Event("sambal:session-started"));
      const nextPolicy = await requestJson<Policy>(
        `/channel/sessions/${created.session_id}/policy`,
        {},
        created.session_token,
      );
      setPolicy(nextPolicy);
      setContinued(Boolean(nextPolicy.intake_ready));
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "We could not start safely. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  };

  const loadPolicy = async (activeSession = session) => {
    if (!activeSession) return null;
    const nextPolicy = await requestJson<Policy>(
      `/channel/sessions/${activeSession.session_id}/policy`,
      {},
      activeSession.session_token,
    );
    setPolicy(nextPolicy);
    setContinued(Boolean(nextPolicy.intake_ready));
    return nextPolicy;
  };

  const continueIntake = async () => {
    if (!session || !policy) return;
    setBusy(true);
    setError("");
    try {
      await requestJson(
        `/channel/sessions/${session.session_id}/intake/continue`,
        {
          method: "POST",
          body: JSON.stringify({
            policy_version: policy.policy_version,
            client_action_id: clientId("continue"),
          }),
        },
        session.session_token,
      );
      const nextPolicy = await loadPolicy();
      setContinued(Boolean(nextPolicy?.intake_ready));
    } catch (cause) {
      if (cause instanceof RequestError && cause.status === 409) {
        try {
          await loadPolicy();
        } catch {
          // Keep the original error if the policy cannot be refreshed.
        }
        setContinued(false);
        setError("The notice was updated. Please review it again.");
      } else {
        setError(
          cause instanceof Error
            ? cause.message
            : "We could not record your choice.",
        );
      }
    } finally {
      setBusy(false);
    }
  };

  const chooseMode = async (nextMode: IntakeMode) => {
    if (!session) return;
    setBusy(true);
    setError("");
    try {
      await requestJson(
        `/channel/sessions/${session.session_id}/mode`,
        {
          method: "POST",
          body: JSON.stringify({ interaction_mode: nextMode }),
        },
        session.session_token,
      );
      await loadPolicy();
      router.push(
        nextMode === "TEXT"
          ? "/help/write"
          : nextMode === "SILENT"
            ? "/help/silent"
            : "/help/speak",
      );
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "We could not choose that option.",
      );
    } finally {
      setBusy(false);
    }
  };

  const submit = async (kind: "write" | "silent") => {
    if (!session) return;
    setBusy(true);
    setError("");
    const submissionId = submissionIds[kind];
    if (!submissionId) return;
    const body =
      kind === "write"
        ? {
            client_submission_id: submissionId,
            narrative: draft.narrative,
            optional_when: draft.optional_when || undefined,
            optional_location: draft.optional_location || undefined,
            optional_current_safety: draft.optional_current_safety || undefined,
            optional_contact_preference:
              draft.optional_contact_preference || undefined,
            optional_contact_value: draft.optional_contact_value || undefined,
          }
        : {
            client_submission_id: submissionId,
            current_safety: silent.current_safety,
            urgent_help: silent.urgent_help,
            contact_preference: silent.contact_preference,
            optional_contact_value: silent.optional_contact_value || undefined,
          };
    try {
      const result = await requestJson<Receipt>(
        `/intake/sessions/${session.session_id}/${kind}`,
        { method: "POST", body: JSON.stringify(body) },
        session.session_token,
      );
      window.sessionStorage.removeItem(DRAFT_KEY);
      window.sessionStorage.removeItem(SESSION_KEY);
      window.sessionStorage.removeItem(
        kind === "write" ? WRITE_SUBMISSION_KEY : SILENT_SUBMISSION_KEY,
      );
      window.dispatchEvent(new Event("sambal:session-ended"));
      window.sessionStorage.setItem(RECEIPT_KEY, JSON.stringify(result));
      setReceipt(result);
      router.push("/help/received");
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "We could not save this yet. Your draft remains on this device.",
      );
    } finally {
      setBusy(false);
    }
  };

  const back = (
    <Link className="citizen-back" href="/help">
      <ArrowLeft aria-hidden="true" /> Back to choices
    </Link>
  );

  if (mode === "received") {
    return <ReceiptView receipt={receipt} />;
  }

  if (hydrating) {
    return (
      <div className="citizen-flow" aria-live="polite">
        <h1 tabIndex={-1}>Restoring your private session</h1>
        <p>Please wait while we check the session on this device.</p>
      </div>
    );
  }

  if (sessionExpired) {
    return (
      <div className="citizen-flow">
        <p className="eyebrow">Private session ended</p>
        <h1 tabIndex={-1}>Your saved words are still here</h1>
        <p className="citizen-lead">
          This short-lived session expired. Your draft was kept only on this
          device; start a new private session when it is safe.
        </p>
        {error ? <FieldError>{error}</FieldError> : null}
        <Button size="lg" onClick={begin} loading={busy}>
          Start a new private session
        </Button>
      </div>
    );
  }

  if (mode === "help") {
    return (
      <div className="citizen-flow">
        <p className="eyebrow">A private place to begin</p>
        <h1 tabIndex={-1}>How would you like to share?</h1>
        <p className="citizen-lead">
          You choose what feels safest. You do not need to know the right words,
          prove anything, or provide your name.
        </p>
        {!hasSession ? (
          <Card className="citizen-start-card">
            <CardContent className="citizen-stack">
              <ShieldCheck aria-hidden="true" />
              <h2>Start a private session</h2>
              <p>
                A short-lived session lets us protect this conversation. It is
                created only when you choose to begin.
              </p>
              <Button size="lg" onClick={begin} loading={busy}>
                Start safely
              </Button>
            </CardContent>
          </Card>
        ) : null}
        {error ? <FieldError>{error}</FieldError> : null}
        {policy ? <Notice policy={policy} /> : null}
        {policy && !continued ? (
          <Button size="lg" onClick={continueIntake} loading={busy}>
            I understand — show me the choices <ArrowRight aria-hidden="true" />
          </Button>
        ) : null}
        {continued ? <ModeChoices busy={busy} onChoose={chooseMode} /> : null}
      </div>
    );
  }

  if (!hasSession) {
    return (
      <div className="citizen-flow">
        <h1 tabIndex={-1}>Let’s begin safely</h1>
        <p>Start a private session before choosing an intake method.</p>
        <LinkButton href="/help" size="lg">
          Go to safe start <ArrowRight aria-hidden="true" />
        </LinkButton>
      </div>
    );
  }

  if (mode === "speak") {
    return (
      <div className="citizen-flow">
        {back}
        <p className="eyebrow">Speak</p>
        <h1 tabIndex={-1}>Speak is not active yet</h1>
        <p className="citizen-lead">
          Voice capture and speech recognition have not started. No microphone,
          recording, or audio upload is used on this page.
        </p>
        <div className="truth-callout">
          <strong>Nothing is listening.</strong>
          <span>You can use Write or Silent intake instead.</span>
        </div>
        <div className="citizen-actions">
          <Button size="lg" onClick={() => chooseMode("TEXT")} loading={busy}>
            Write instead
          </Button>
          <Button
            variant="secondary"
            size="lg"
            onClick={() => chooseMode("SILENT")}
            loading={busy}
          >
            Use Silent intake
          </Button>
        </div>
      </div>
    );
  }

  if (mode === "write") {
    return (
      <WriteFlow
        draft={draft}
        updateDraft={updateDraft}
        step={writeStep}
        setStep={setWriteStep}
        busy={busy}
        error={error}
        onSubmit={() => submit("write")}
        back={back}
      />
    );
  }

  return (
    <SilentFlow
      silent={silent}
      setSilent={setSilent}
      step={silentStep}
      setStep={setSilentStep}
      busy={busy}
      error={error}
      onSubmit={() => submit("silent")}
      back={back}
    />
  );
}

function ModeChoices({
  busy,
  onChoose,
}: {
  busy: boolean;
  onChoose: (mode: IntakeMode) => void;
}) {
  const choices = useMemo(
    () =>
      [
        [
          "TEXT",
          "Write",
          "Share in your own words. You can review before sending.",
        ],
        [
          "VOICE",
          "Speak",
          "Voice capture is not active yet. Nothing will listen.",
        ],
        [
          "SILENT",
          "Silent",
          "Answer a few quiet, one-question-at-a-time prompts.",
        ],
      ] as const,
    [],
  );
  return (
    <section className="mode-choices" aria-labelledby="mode-heading">
      <h2 id="mode-heading">Choose how to continue</h2>
      <div className="mode-choices__grid">
        {choices.map(([value, label, description]) => (
          <button
            type="button"
            className="mode-card"
            key={value}
            onClick={() => onChoose(value)}
            disabled={busy}
          >
            <strong>{label}</strong>
            <span>{description}</span>
            <ArrowRight aria-hidden="true" />
          </button>
        ))}
      </div>
    </section>
  );
}

function WriteFlow({
  draft,
  updateDraft,
  step,
  setStep,
  busy,
  error,
  onSubmit,
  back,
}: {
  draft: WriteDraft;
  updateDraft: (key: keyof WriteDraft, value: string) => void;
  step: "form" | "review";
  setStep: (step: "form" | "review") => void;
  busy: boolean;
  error: string;
  onSubmit: () => void;
  back: React.ReactNode;
}) {
  if (step === "review")
    return (
      <div className="citizen-flow">
        {back}
        <p className="eyebrow">Write · Review</p>
        <h1 tabIndex={-1}>Review before sending</h1>
        <p className="citizen-lead">
          You can go back and change anything. Only the information shown below
          will be sent.
        </p>
        <div className="review-card">
          <h2>Your words</h2>
          <p className="review-narrative">{draft.narrative}</p>
          {draft.optional_when ? (
            <p>
              <strong>When:</strong> {draft.optional_when}
            </p>
          ) : null}
          {draft.optional_location ? (
            <p>
              <strong>Where:</strong> {draft.optional_location}
            </p>
          ) : null}
          {draft.optional_contact_preference ? (
            <p>
              <strong>Contact preference:</strong>{" "}
              {draft.optional_contact_preference || "Not specified"}
            </p>
          ) : null}
          {draft.optional_contact_value ? (
            <p>
              <strong>Contact detail:</strong> {draft.optional_contact_value}
            </p>
          ) : null}
        </div>
        {error ? <FieldError>{error}</FieldError> : null}
        <div className="citizen-actions">
          <Button variant="secondary" onClick={() => setStep("form")}>
            Edit
          </Button>
          <Button onClick={onSubmit} loading={busy}>
            Send securely
          </Button>
        </div>
      </div>
    );
  return (
    <div className="citizen-flow">
      {back}
      <p className="eyebrow">Write</p>
      <h1 tabIndex={-1}>Tell us what you want us to know</h1>
      <p className="citizen-lead">
        Use your own words. You can leave optional questions blank.
      </p>
      <form
        className="citizen-form"
        onSubmit={(event) => {
          event.preventDefault();
          if (draft.narrative.trim()) setStep("review");
        }}
      >
        <FormField
          label="What happened?"
          required
          helperText="You can write up to 16,000 characters. Do not include anything you do not want to share."
        >
          <Textarea
            value={draft.narrative}
            onChange={(event) => updateDraft("narrative", event.target.value)}
            maxLength={16000}
            rows={10}
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="sentences"
          />
        </FormField>
        <div className="citizen-form__grid">
          <FormField label="When did this happen?" helperText="Optional">
            <Input
              value={draft.optional_when}
              onChange={(event) =>
                updateDraft("optional_when", event.target.value)
              }
              maxLength={160}
              autoComplete="off"
            />
          </FormField>
          <FormField label="Where did this happen?" helperText="Optional">
            <Input
              value={draft.optional_location}
              onChange={(event) =>
                updateDraft("optional_location", event.target.value)
              }
              maxLength={300}
              autoComplete="off"
            />
          </FormField>
        </div>
        <div className="citizen-form__grid">
          <FormField label="Current safety" helperText="Optional">
            <select
              className="control"
              value={draft.optional_current_safety}
              onChange={(event) =>
                updateDraft("optional_current_safety", event.target.value)
              }
            >
              <option value="">Prefer not to say</option>
              <option value="YES">I am safe now</option>
              <option value="NO_SOMEONE_MAY_BE_NEARBY">
                Someone may be nearby
              </option>
              <option value="NOT_SURE">Not sure</option>
              <option value="SKIP">Skip</option>
            </select>
          </FormField>
          <FormField label="Contact preference" helperText="Optional">
            <select
              className="control"
              value={draft.optional_contact_preference}
              onChange={(event) =>
                updateDraft("optional_contact_preference", event.target.value)
              }
            >
              <option value="">No preference yet</option>
              <option value="DO_NOT_CALL">Do not call</option>
              <option value="SILENT_SMS_PREFERRED">Silent SMS preferred</option>
              <option value="WHATSAPP_PREFERRED">WhatsApp preferred</option>
              <option value="ASK_ME_LATER">Ask me later</option>
              <option value="NO_CONTACT_DETAILS_NOW">
                No contact details now
              </option>
            </select>
          </FormField>
        </div>
        <FormField
          label="Contact detail"
          helperText="Optional. Add this only if it is safe to use."
        >
          <Input
            value={draft.optional_contact_value}
            onChange={(event) =>
              updateDraft("optional_contact_value", event.target.value)
            }
            maxLength={320}
            autoComplete="off"
          />
        </FormField>
        {error ? <FieldError>{error}</FieldError> : null}
        <Button type="submit" size="lg">
          Review
        </Button>
      </form>
    </div>
  );
}

const silentValueLabels: Record<string, string> = {
  YES: "Yes",
  NO: "No",
  NO_SOMEONE_MAY_BE_NEARBY: "No — someone may be nearby",
  NOT_SURE: "Not sure",
  SKIP: "Skip",
  YES_AS_SOON_AS_POSSIBLE: "Yes, as soon as possible",
  DO_NOT_CALL: "Do not call",
  SILENT_SMS_PREFERRED: "Silent SMS preferred",
  WHATSAPP_PREFERRED: "WhatsApp preferred",
  ASK_ME_LATER: "Ask me later",
  NO_CONTACT_DETAILS_NOW: "No contact details now",
};

function humanizeSilentValue(value: string) {
  return silentValueLabels[value] || value || "Not answered";
}

function SilentFlow({
  silent,
  setSilent,
  step,
  setStep,
  busy,
  error,
  onSubmit,
  back,
}: {
  silent: {
    current_safety: string;
    urgent_help: string;
    contact_preference: string;
    optional_contact_value: string;
  };
  setSilent: React.Dispatch<
    React.SetStateAction<{
      current_safety: string;
      urgent_help: string;
      contact_preference: string;
      optional_contact_value: string;
    }>
  >;
  step: number;
  setStep: (step: number) => void;
  busy: boolean;
  error: string;
  onSubmit: () => void;
  back: React.ReactNode;
}) {
  const update = (key: keyof typeof silent, value: string) =>
    setSilent((current) => ({ ...current, [key]: value }));
  const questions = [
    {
      key: "current_safety",
      title: "Are you safe to continue right now?",
      options: [
        ["YES", "Yes"],
        ["NO_SOMEONE_MAY_BE_NEARBY", "No — someone may be nearby"],
        ["NOT_SURE", "Not sure"],
        ["SKIP", "Skip"],
      ],
    },
    {
      key: "urgent_help",
      title: "Do you need help as soon as possible?",
      options: [
        ["YES_AS_SOON_AS_POSSIBLE", "Yes, as soon as possible"],
        ["NO", "No"],
        ["NOT_SURE", "Not sure"],
        ["SKIP", "Skip"],
      ],
    },
    {
      key: "contact_preference",
      title: "What contact feels safest?",
      options: [
        ["DO_NOT_CALL", "Do not call"],
        ["SILENT_SMS_PREFERRED", "Silent SMS preferred"],
        ["WHATSAPP_PREFERRED", "WhatsApp preferred"],
        ["ASK_ME_LATER", "Ask me later"],
        ["NO_CONTACT_DETAILS_NOW", "No contact details now"],
      ],
    },
  ] as const;
  const question = questions[step];
  if (step < questions.length)
    return (
      <div className="citizen-flow">
        {back}
        <p className="eyebrow">Silent · Question {step + 1} of 3</p>
        <h1 tabIndex={-1}>{question.title}</h1>
        <div className="choice-stack">
          {question.options.map(([value, label]) => (
            <ChoiceButton
              key={value}
              value={value}
              label={label}
              selected={silent[question.key]}
              onClick={(next) => {
                update(question.key, next);
                setStep(step + 1);
              }}
            />
          ))}
        </div>
        <p className="citizen-step-note">
          One question at a time. You can stop whenever you need to.
        </p>
      </div>
    );
  if (step === questions.length)
    return (
      <div className="citizen-flow">
        {back}
        <p className="eyebrow">Silent · Optional</p>
        <h1 tabIndex={-1}>Would you like to leave a safe contact detail?</h1>
        <p className="citizen-lead">
          You can skip this. Choose “Do not call” or “No contact details now” if
          contact would not be safe.
        </p>
        <FormField label="Contact detail" helperText="Optional. One line only.">
          <Input
            value={silent.optional_contact_value}
            onChange={(event) =>
              update("optional_contact_value", event.target.value)
            }
            maxLength={320}
            autoComplete="off"
          />
        </FormField>
        {error ? <FieldError>{error}</FieldError> : null}
        <div className="citizen-actions">
          <Button variant="secondary" onClick={() => setStep(2)}>
            Back
          </Button>
          <Button size="lg" onClick={() => setStep(4)}>
            Review
          </Button>
        </div>
      </div>
    );
  return (
    <div className="citizen-flow">
      {back}
      <p className="eyebrow">Silent · Review</p>
      <h1 tabIndex={-1}>Review your answers</h1>
      <div className="review-card">
        <p>
          <strong>Current safety:</strong>{" "}
          {humanizeSilentValue(silent.current_safety)}
        </p>
        <p>
          <strong>Urgent help:</strong>{" "}
          {humanizeSilentValue(silent.urgent_help)}
        </p>
        <p>
          <strong>Contact preference:</strong>{" "}
          {humanizeSilentValue(silent.contact_preference)}
        </p>
        {silent.optional_contact_value ? (
          <p>
            <strong>Contact detail:</strong> {silent.optional_contact_value}
          </p>
        ) : null}
      </div>
      {error ? <FieldError>{error}</FieldError> : null}
      <div className="citizen-actions">
        <Button variant="secondary" onClick={() => setStep(3)}>
          Edit
        </Button>
        <Button onClick={onSubmit} loading={busy}>
          Send securely
        </Button>
      </div>
    </div>
  );
}

function ReceiptView({ receipt }: { receipt: Receipt | null }) {
  const [copied, setCopied] = useState(false);
  if (!receipt)
    return (
      <div className="citizen-flow">
        <h1 tabIndex={-1}>No receipt on this device</h1>
        <p>Start again if you still want to share something.</p>
        <LinkButton href="/help" size="lg">
          Start a new session
        </LinkButton>
      </div>
    );
  return (
    <div className="citizen-flow citizen-flow--receipt">
      <p className="eyebrow">Received</p>
      <h1 tabIndex={-1}>Your information was received</h1>
      <p className="citizen-lead">
        Keep this reference if you want to talk about this submission later. It
        does not reveal the contents of what you shared.
      </p>
      <div className="receipt-reference">
        <span>Reference</span>
        <strong>{receipt.tracking_reference}</strong>
        <Button
          variant="secondary"
          onClick={() => {
            void navigator.clipboard?.writeText(receipt.tracking_reference);
            setCopied(true);
          }}
        >
          <Copy aria-hidden="true" /> {copied ? "Copied" : "Copy reference"}
        </Button>
      </div>
      <p className="receipt-meta">
        Received {new Date(receipt.received_at).toLocaleString()} ·{" "}
        {receipt.entry_count} item{receipt.entry_count === 1 ? "" : "s"}
      </p>
      <div className="citizen-actions">
        <Button variant="secondary" onClick={() => window.print()}>
          Print
        </Button>
        <LinkButton href="/" variant="quiet">
          Leave this page
        </LinkButton>
      </div>
      <p className="citizen-truth">
        This prototype does not provide emergency dispatch, legal advice,
        diagnosis, or a guarantee of response time.
      </p>
    </div>
  );
}
