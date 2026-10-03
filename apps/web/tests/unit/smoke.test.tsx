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
      "A clear, humane grammar for future public-service workflows",
    );
  });

  it("renders capability states with truthful badges", () => {
    render(React.createElement(HomePage));
    expect(screen.getByText("Design system")).toBeDefined();
    expect(screen.getByText("Accessibility automated baseline")).toBeDefined();
    expect(screen.getByText("Citizen intake")).toBeDefined();
    expect(screen.getByText("AI assessment")).toBeDefined();
  });

  it("renders engineering notes and capability status indicators", () => {
    render(React.createElement(HomePage));
    expect(
      screen.getByText(/Civic Calm tokens and reusable primitives are ready/i),
    ).toBeDefined();
    expect(
      screen.getByText(
        /No live scoring, diagnosis, or model inference exists/i,
      ),
    ).toBeDefined();
  });
});
