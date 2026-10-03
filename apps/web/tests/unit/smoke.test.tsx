import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import HomePage from "../../src/app/page";

describe("HomePage Smoke Test", () => {
  it("renders the main heading correctly with single h1", () => {
    render(React.createElement(HomePage));
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeDefined();
    expect(heading).not.toBeNull();
    expect(heading.textContent).toContain(
      "SAMBAL Intelligence & Response Layer — Architecture & Foundation Status",
    );
  });

  it("renders capability states with truthful badges", () => {
    render(React.createElement(HomePage));
    expect(screen.getByText("Monorepo Toolchain & App Shells")).toBeDefined();
    expect(screen.getByText("Canonical PostgreSQL Engine")).toBeDefined();
    expect(screen.getByText("Speech-to-Text Pipeline (ASR)")).toBeDefined();
    expect(
      screen.getByText("Stress & Vulnerability Index (SVI)"),
    ).toBeDefined();
  });

  it("renders engineering notes and capability status indicators", () => {
    render(React.createElement(HomePage));
    expect(
      screen.getByText(
        /Clean-CI verified across unit, E2E, and Axe a11y test suites/i,
      ),
    ).toBeDefined();
    expect(
      screen.getByText(
        /Requires Packet 08 benchmarking against IndicConformer\/Bhashini/i,
      ),
    ).toBeDefined();
  });
});
