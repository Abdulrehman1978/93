import { fireEvent, render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  Button,
  Dialog,
  ErrorSummary,
  focusFirstInvalid,
  FormField,
  Input,
  LanguageSelector,
  StatusBadge,
  Tabs,
  Tooltip,
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

  it("preserves consumer descriptors and synchronizes required state", () => {
    render(
      <>
        <span id="consumer-note">Consumer supplied guidance.</span>
        <FormField
          label="Synthetic reference"
          helperText="Use demonstration data only."
          error="Enter a synthetic reference."
          required
        >
          <Input aria-describedby="consumer-note" />
        </FormField>
      </>,
    );
    const input = screen.getByLabelText(/Synthetic reference/);
    expect(input).toHaveAttribute(
      "aria-describedby",
      expect.stringContaining("consumer-note"),
    );
    expect(input).toHaveAttribute("required");
    expect(input).toHaveAttribute("aria-required", "true");
  });

  it("renders truth status as text plus a semantic icon", () => {
    render(<StatusBadge status="PROVISIONAL" />);
    expect(screen.getByText("PROVISIONAL")).toBeVisible();
    expect(screen.getByText("PROVISIONAL").querySelector("svg")).not.toBeNull();
  });

  it("filters and selects native language names with the keyboard", () => {
    render(<LanguageSelector />);
    const search = screen.getByRole("combobox", { name: "Language" });
    fireEvent.change(search, { target: { value: "Urdu" } });
    expect(search).toHaveAttribute(
      "aria-activedescendant",
      expect.stringContaining("option-ur"),
    );
    fireEvent.keyDown(search, { key: "Enter" });
    expect(screen.getByText(/Selected:/)).toHaveTextContent("اردو · Urdu");
    expect(screen.getByRole("option", { name: /اردو Urdu/ })).toHaveAttribute(
      "aria-selected",
      "true",
    );
  });

  it("announces language arrow navigation through active descendant", () => {
    render(<LanguageSelector />);
    const search = screen.getByRole("combobox", { name: "Language" });
    const initial = search.getAttribute("aria-activedescendant");
    fireEvent.keyDown(search, { key: "ArrowDown" });
    expect(search.getAttribute("aria-activedescendant")).not.toBe(initial);
    expect(search).toHaveAttribute("aria-controls");
    expect(screen.getByRole("listbox")).toHaveAttribute(
      "id",
      search.getAttribute("aria-controls"),
    );
  });

  it("gives a tooltip trigger one focus stop and preserves its name", () => {
    render(
      <Tooltip label="Extra synthetic context">
        <Button>More context</Button>
      </Tooltip>,
    );
    const trigger = screen.getByRole("button", { name: "More context" });
    expect(trigger).not.toHaveAttribute("tabindex", "0");
    expect(trigger).toHaveAttribute("aria-describedby");
    expect(screen.getByRole("tooltip")).toHaveTextContent(
      "Extra synthetic context",
    );
    expect(trigger.closest(".tooltip")).not.toBeNull();
  });

  it("focuses the error summary and follows error links", () => {
    render(
      <>
        <ErrorSummary
          errors={[{ fieldId: "invalid-name", message: "Enter a name." }]}
        />
        <Input id="invalid-name" />
      </>,
    );
    expect(screen.getByRole("heading", { name: /check/i })).toHaveFocus();
    fireEvent.click(screen.getByRole("link", { name: "Enter a name." }));
    expect(screen.getByRole("textbox")).toHaveFocus();
  });

  it("focuses the first invalid control with the reusable helper", () => {
    const { container } = render(
      <div>
        <Input id="first-invalid" aria-invalid="true" />
        <Input id="second-invalid" aria-invalid="true" />
      </div>,
    );
    expect(focusFirstInvalid(container)?.id).toBe("first-invalid");
    expect(document.activeElement).toBe(
      container.querySelector("#first-invalid"),
    );
  });

  it("supports Home and End tabs and safely renders empty tabs", () => {
    const items = [
      { id: "one", label: "One", content: "First" },
      { id: "two", label: "Two", content: "Second" },
    ];
    const { rerender } = render(<Tabs items={items} label="Examples" />);
    const tabs = screen.getAllByRole("tab");
    tabs[0].focus();
    fireEvent.keyDown(tabs[0], { key: "End" });
    expect(tabs[1]).toHaveFocus();
    fireEvent.keyDown(tabs[1], { key: "Home" });
    expect(tabs[0]).toHaveFocus();
    rerender(<Tabs items={[]} label="Empty examples" />);
    expect(screen.queryByRole("tablist")).not.toBeInTheDocument();
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
    expect(screen.getByRole("button", { name: "Close dialog" })).toHaveFocus();
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
