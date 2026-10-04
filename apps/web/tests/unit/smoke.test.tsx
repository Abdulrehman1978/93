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
      "You can share what is happening in the way that feels safest",
    );
  });

  it("renders truthful citizen intake affordances", () => {
    render(React.createElement(HomePage));
    expect(screen.getByRole("link", { name: /get help/i })).toBeDefined();
    expect(screen.getByText("Private by design")).toBeDefined();
    expect(screen.getByText("Human-readable choices")).toBeDefined();
  });

  it("renders the prototype boundary", () => {
    render(React.createElement(HomePage));
    expect(
      screen.getByText(/No microphone is used by the Speak page/i),
    ).toBeDefined();
    expect(
      screen.getByText(/Quick Exit is available throughout the intake flow/i),
    ).toBeDefined();
  });
});
