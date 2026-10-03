import { ArrowRight, Blocks, ShieldCheck } from "lucide-react";
import {
  Card,
  CardContent,
  LinkButton,
  PageHeader,
  PublicShell,
  StatusBadge,
} from "@/components";

const capabilities = [
  [
    "Design system",
    "FOUNDATION_READY",
    "Civic Calm tokens and reusable primitives are ready for feature teams.",
  ],
  [
    "Accessibility automated baseline",
    "LIVE",
    "Keyboard, Axe, reduced-motion, mobile, and RTL checks run in CI.",
  ],
  [
    "Citizen intake",
    "NOT_STARTED",
    "Citizen workflow behavior begins only after Packet 06 and its approval gates.",
  ],
  [
    "AI assessment",
    "NOT_STARTED",
    "No live scoring, diagnosis, or model inference exists in this foundation.",
  ],
] as const;

export default function HomePage() {
  return (
    <PublicShell>
      <div className="showcase">
        <PageHeader
          eyebrow="Civic Calm foundation"
          title="A clear, humane grammar for future public-service workflows"
          description="SAMBAL is an SIH prototype for future NHAA integration. This foundation demonstrates truthful capability states, accessible interaction patterns, and restrained civic visual design—not a live citizen service."
          actions={
            <LinkButton id="view-health-btn" href="/design-system" size="lg">
              Review design system <ArrowRight aria-hidden="true" />
            </LinkButton>
          }
        />

        <section aria-labelledby="foundation-heading" className="panel">
          <div className="section-header">
            <p className="eyebrow">Packet 05</p>
            <h2 id="foundation-heading">Foundation state</h2>
            <p>
              Reusable components are live. Product workflows remain
              deliberately unimplemented.
            </p>
          </div>
          <div className="showcase-grid">
            {capabilities.map(([name, status, description]) => (
              <Card key={name}>
                <CardContent className="showcase-stack">
                  {name === "Design system" ? (
                    <Blocks aria-hidden="true" />
                  ) : (
                    <ShieldCheck aria-hidden="true" />
                  )}
                  <h3>{name}</h3>
                  <StatusBadge status={status} />
                  <p>{description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </PublicShell>
  );
}
