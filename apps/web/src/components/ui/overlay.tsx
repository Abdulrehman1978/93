"use client";

import { useId, useRef, type ReactNode } from "react";
import { ChevronDown, Info, X } from "lucide-react";
import { Button, IconButton } from "./button";

export function Tooltip({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  const id = useId();
  return (
    <span className="tooltip">
      <span aria-describedby={id} tabIndex={0} className="tooltip__trigger">
        {children}
      </span>
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
  const titleId = useId();
  const descriptionId = useId();

  const close = () => dialogRef.current?.close();

  return (
    <>
      <Button
        ref={triggerRef}
        variant="danger"
        onClick={() => dialogRef.current?.showModal()}
      >
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
