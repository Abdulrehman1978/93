import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";

export function Surface({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("surface", className)} {...props} />;
}

export function Panel({ className, ...props }: HTMLAttributes<HTMLElement>) {
  return <section className={cn("panel", className)} {...props} />;
}

export function Card({ className, ...props }: HTMLAttributes<HTMLElement>) {
  return <article className={cn("card", className)} {...props} />;
}

export function CardHeader({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("card__header", className)} {...props} />;
}

export function CardContent({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("card__content", className)} {...props} />;
}

export function CardFooter({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("card__footer", className)} {...props} />;
}

export function Divider({
  className,
  ...props
}: HTMLAttributes<HTMLHRElement>) {
  return <hr className={cn("divider", className)} {...props} />;
}
