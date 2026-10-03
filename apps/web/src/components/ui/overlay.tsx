"use client";

import {
  cloneElement,
  useId,
  useRef,
  type ReactElement,
  type ReactNode,
} from "react";
import { ChevronDown, Info, X } from "lucide-react";
import { Button, IconButton } from "./button";
import { cn } from "@/lib/cn";

function mergeIds(...values: Array<string | undefined>) {
  return (
    Array.from(
      new Set(
        values.flatMap((value) => value?.split(/\s+/) ?? []).filter(Boolean),
      ),
    ).join(" ") || undefined
  );
}

export function Tooltip({
  label,
  children,
}: {
  label: string;
  children: ReactElement<{
    "aria-describedby"?: string;
    className?: string;
  }>;
}) {
  const id = useId();
  const trigger = cloneElement(children, {
    "aria-describedby": mergeIds(children.props["aria-describedby"], id),
    className: cn(children.props.className, "tooltip__trigger"),
  });
  return (
    <span className="tooltip">
      {trigger}
      <span id={id} role="tooltip" className="tooltip__content">
        {label}
      </span>
    </span>
  );
}

export function Popover({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <details className="popover">
      <summary className="button button--secondary button--md">
        {label} <ChevronDown aria-hidden="true" />
      </summary>
      <div className="popover__content">{children}</div>
    </details>
  );
}

export function Dialog({
  title,
  description,
  triggerLabel,
}: {
  title: string;
  description: string;
  triggerLabel: string;
}) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const titleId = useId();
  const descriptionId = useId();

  const close = () => dialogRef.current?.close();
  const open = () => {
    dialogRef.current?.showModal();
    closeRef.current?.focus();
  };

  return (
    <>
      <Button ref={triggerRef} variant="danger" onClick={open}>
        {triggerLabel}
      </Button>
      <dialog
        ref={dialogRef}
        className="dialog"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
        onClose={() => triggerRef.current?.focus()}
        onClick={(event) => {
          if (event.target === dialogRef.current) close();
        }}
      >
        <div className="dialog__panel">
          <IconButton
            ref={closeRef}
            label="Close dialog"
            className="dialog__close"
            onClick={close}
          >
            <X />
          </IconButton>
          <Info aria-hidden="true" className="dialog__symbol" />
          <h2 id={titleId}>{title}</h2>
          <p id={descriptionId}>{description}</p>
          <div className="dialog__actions">
            <Button variant="secondary" onClick={close}>
              Keep example
            </Button>
            <Button variant="danger" onClick={close}>
              Remove synthetic example
            </Button>
          </div>
        </div>
      </dialog>
    </>
  );
}
