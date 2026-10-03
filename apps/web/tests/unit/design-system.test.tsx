import { fireEvent, render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  Button,
  Dialog,
  FormField,
  Input,
  LanguageSelector,
  StatusBadge,
} from "../../src/components";

describe("Civic Calm primitives", () => {
  it("preserves button content while loading and exposes busy state", () => {
    render(<Button loading>Save draft</Button>);
    const button = screen.getByRole("button", { name: "Save draft" });
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent("Save draft");
  });

  it("automatically associates form help and plain-language errors", () => {
    render(
      <FormField
        label="Synthetic reference"
        helperText="Use demonstration data only."
        error="Enter a synthetic reference."
        required
      >
        <Input />
      </FormField>,
    );
    const input = screen.getByLabelText(/Synthetic reference/);
    const describedBy = input.getAttribute("aria-describedby") ?? "";
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(describedBy.split(" ")).toHaveLength(2);
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Enter a synthetic reference.",
    );
  });

  it("renders truth status as text plus a semantic icon", () => {
    render(<StatusBadge status="PROVISIONAL" />);
    expect(screen.getByText("PROVISIONAL")).toBeVisible();
    expect(screen.getByText("PROVISIONAL").querySelector("svg")).not.toBeNull();
  });

  it("filters and selects native language names with the keyboard", () => {
    render(<LanguageSelector />);
    const search = screen.getByRole("searchbox", { name: "Language" });
    fireEvent.change(search, { target: { value: "Urdu" } });
    fireEvent.keyDown(search, { key: "Enter" });
    expect(screen.getByText(/Selected:/)).toHaveTextContent("اردو · Urdu");
  });

  it("opens and closes the confirmation dialog while restoring focus", () => {
    HTMLDialogElement.prototype.showModal = function showModal() {
      this.open = true;
    };
    HTMLDialogElement.prototype.close = function close() {
      this.open = false;
      this.dispatchEvent(new Event("close"));
    };
    render(
      <Dialog
        title="Remove example?"
        description="Only the synthetic fixture is affected."
        triggerLabel="Remove example"
      />,
    );
    const trigger = screen.getByRole("button", { name: "Remove example" });
    trigger.focus();
    fireEvent.click(trigger);
    expect(screen.getByRole("dialog")).toHaveAttribute("open");
    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));
    expect(trigger).toHaveFocus();
  });
});

describe("semantic design tokens", () => {
  it("keeps the required public token contract", () => {
    const cssPath = resolve(process.cwd(), "src/app/globals.css");
    const css = readFileSync(cssPath, "utf8");
    for (const token of [
      "--background",
      "--surface",
      "--foreground",
      "--primary",
      "--border",
      "--focus",
      "--info",
      "--success",
      "--warning",
      "--danger",
      "--risk-low",
      "--risk-moderate",
      "--risk-high",
      "--risk-critical",
    ]) {
      expect(css).toContain(`${token}:`);
    }
  });
});
