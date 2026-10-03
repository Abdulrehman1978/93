import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SAMBAL — Civic service prototype",
  description:
    "SIH prototype design and engineering foundation for SAMBAL/NHAA integration.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
