import type {
  AnchorHTMLAttributes,
  ButtonHTMLAttributes,
  ReactNode,
} from "react";
import { forwardRef } from "react";
import { LoaderCircle } from "lucide-react";
import { cn } from "@/lib/cn";
import { VisuallyHidden } from "@/components/accessibility";

export type ButtonVariant =
  "primary" | "secondary" | "tertiary" | "danger" | "quiet";
export type ButtonSize = "sm" | "md" | "lg";

const buttonClass = (
  variant: ButtonVariant,
  size: ButtonSize,
  className?: string,
) => cn("button", `button--${variant}`, `button--${size}`, className);

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
    size?: ButtonSize;
    loading?: boolean;
  }
>(function Button(
  {
    variant = "primary",
    size = "md",
    loading = false,
    disabled,
    children,
    className,
    ...props
  },
  ref,
) {
  return (
    <button
      ref={ref}
      className={buttonClass(variant, size, className)}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading ? (
        <LoaderCircle aria-hidden="true" className="button__spinner" />
      ) : null}
      <span
        className={cn("button__label", loading && "button__label--loading")}
      >
        {children}
      </span>
    </button>
  );
});

export const IconButton = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & {
    label: string;
    variant?: ButtonVariant;
    size?: ButtonSize;
    children: ReactNode;
  }
>(function IconButton(
  { label, variant = "quiet", size = "md", children, className, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      className={cn(buttonClass(variant, size, className), "button--icon")}
      aria-label={label}
      {...props}
    >
      <span aria-hidden="true">{children}</span>
      <VisuallyHidden>{label}</VisuallyHidden>
    </button>
  );
});

export function LinkButton({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: AnchorHTMLAttributes<HTMLAnchorElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
}) {
  return (
    <a className={buttonClass(variant, size, className)} {...props}>
      {children}
    </a>
  );
}
