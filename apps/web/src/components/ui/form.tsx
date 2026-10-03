import {
  Children,
  cloneElement,
  useId,
  type FieldsetHTMLAttributes,
  type HTMLAttributes,
  type InputHTMLAttributes,
  type LabelHTMLAttributes,
  type ReactElement,
  type ReactNode,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
} from "react";
import { cn } from "@/lib/cn";

export function Label(props: LabelHTMLAttributes<HTMLLabelElement>) {
  return <label {...props} className={cn("field__label", props.className)} />;
}

export function HelperText(props: HTMLAttributes<HTMLParagraphElement>) {
  return <p {...props} className={cn("field__helper", props.className)} />;
}

export function FieldError(props: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      role="alert"
      {...props}
      className={cn("field__error", props.className)}
    />
  );
}

export function FormField({
  label,
  helperText,
  error,
  required,
  children,
  className,
}: {
  label: string;
  helperText?: string;
  error?: string;
  required?: boolean;
  children: ReactElement<{
    id?: string;
    "aria-describedby"?: string;
    "aria-invalid"?: boolean;
  }>;
  className?: string;
}) {
  const generatedId = useId();
  const child = Children.only(children);
  const controlId = child.props.id ?? `field-${generatedId}`;
  const helperId = helperText ? `${controlId}-help` : undefined;
  const errorId = error ? `${controlId}-error` : undefined;
  const describedBy =
    [helperId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <div className={cn("field", className)}>
      <Label htmlFor={controlId}>
        {label}
        {required ? <span className="field__required"> (required)</span> : null}
      </Label>
      {cloneElement(child, {
        id: controlId,
        "aria-describedby": describedBy,
        "aria-invalid": error ? true : undefined,
      })}
      {helperText ? <HelperText id={helperId}>{helperText}</HelperText> : null}
      {error ? <FieldError id={errorId}>{error}</FieldError> : null}
    </div>
  );
}

export function Input({
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn("control", className)} {...props} />;
}

export function Textarea({
  className,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn("control control--textarea", className)}
      {...props}
    />
  );
}

export function Select({
  className,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={cn("control", className)} {...props} />;
}

export function Checkbox({
  label,
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label: ReactNode }) {
  return (
    <label className={cn("choice", className)}>
      <input type="checkbox" {...props} />
      <span>{label}</span>
    </label>
  );
}

export interface RadioOption {
  value: string;
  label: string;
  description?: string;
}

export function RadioGroup({
  legend,
  name,
  options,
  className,
  ...props
}: FieldsetHTMLAttributes<HTMLFieldSetElement> & {
  legend: string;
  name: string;
  options: RadioOption[];
}) {
  return (
    <fieldset className={cn("radio-group", className)} {...props}>
      <legend className="field__label">{legend}</legend>
      {options.map((option) => (
        <label className="choice choice--radio" key={option.value}>
          <input type="radio" name={name} value={option.value} />
          <span>
            <strong>{option.label}</strong>
            {option.description ? <small>{option.description}</small> : null}
          </span>
        </label>
      ))}
    </fieldset>
  );
}
