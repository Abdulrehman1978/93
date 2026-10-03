"use client";

import { useState, type ReactNode } from "react";
import { Button, ErrorSummary, FormField, Input, Select } from "./ui";

const syntheticErrors = [
  {
    fieldId: "synthetic-contact",
    message: "Choose a contact preference.",
  },
  {
    fieldId: "synthetic-language",
    message: "Choose a preferred language.",
  },
];

export function ErrorRecoveryDemo() {
  const [submitted, setSubmitted] = useState(false);

  return (
    <Panel>
      <form
        className="showcase-stack"
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          setSubmitted(true);
        }}
      >
        <ErrorSummary errors={submitted ? syntheticErrors : []} />
        <p className="form-demo__note">
          Synthetic invalid submission: the summary receives focus, then each
          link moves focus to its matching control.
        </p>
        <FormField
          label="Contact preference"
          error={submitted ? syntheticErrors[0].message : undefined}
        >
          <Select id="synthetic-contact" defaultValue="" required>
            <option value="" disabled>
              Select an option
            </option>
            <option value="email">Email</option>
            <option value="phone">Phone</option>
          </Select>
        </FormField>
        <FormField
          label="Preferred language"
          error={submitted ? syntheticErrors[1].message : undefined}
        >
          <Input id="synthetic-language" required />
        </FormField>
        <Button type="submit">Submit synthetic invalid form</Button>
      </form>
    </Panel>
  );
}

function Panel({ children }: { children: ReactNode }) {
  return <div className="error-recovery-demo">{children}</div>;
}
