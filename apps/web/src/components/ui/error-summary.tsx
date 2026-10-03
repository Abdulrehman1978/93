"use client";

import { useEffect, useId, useRef } from "react";

export interface ErrorSummaryItem {
  fieldId: string;
  message: string;
}

export function ErrorSummary({
  errors,
  title = "Please check the highlighted fields",
}: {
  errors: ErrorSummaryItem[];
  title?: string;
}) {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const summaryId = useId();
  const errorSignature = errors
    .map((error) => `${error.fieldId}:${error.message}`)
    .join("|");

  useEffect(() => {
    if (errors.length > 0) headingRef.current?.focus();
  }, [errorSignature, errors.length]);

  if (errors.length === 0) return null;

  return (
    <section
      id={summaryId}
      className="error-summary"
      role="alert"
      aria-labelledby={`${summaryId}-heading`}
    >
      <h2 id={`${summaryId}-heading`} ref={headingRef} tabIndex={-1}>
        {title}
      </h2>
      <ul>
        {errors.map((error) => (
          <li key={error.fieldId}>
            <a
              href={`#${error.fieldId}`}
              onClick={(event) => {
                event.preventDefault();
                document.getElementById(error.fieldId)?.focus();
              }}
            >
              {error.message}
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
