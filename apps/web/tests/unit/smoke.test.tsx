import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import HomePage from "../../src/app/page";

describe("HomePage Smoke Test", () => {
  it("renders the main heading correctly with single h1", () => {
    render(<HomePage />);
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading.textContent).toContain(
      "SAMBAL Real-Time Multilingual Trauma-Aware",
    );
  });

  it("renders all three risk architecture pillars", () => {
    render(<HomePage />);
    expect(screen.getByText("Immediate Safety Gate")).toBeInTheDocument();
    expect(
      screen.getByText("Stress & Vulnerability Index (SVI)"),
    ).toBeInTheDocument();
    expect(screen.getByText("Reported Incident Urgency")).toBeInTheDocument();
  });

  it("renders architectural guardrail labels", () => {
    render(<HomePage />);
    expect(
      screen.getByText(/Provisional triage policy baseline/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Human-in-the-loop ERSS 112 escalation boundary/i),
    ).toBeInTheDocument();
  });
});
