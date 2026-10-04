import { ArrowRight, ShieldCheck } from "lucide-react";
import {
  Card,
  CardContent,
  LinkButton,
  PageHeader,
  PublicShell,
} from "@/components";

export default function HomePage() {
  return (
    <PublicShell>
      <div className="showcase">
        <PageHeader
          eyebrow="A calm place to begin"
          title="You can share what is happening in the way that feels safest"
          description="SAMBAL is a prototype for future civic support. Choose Write, Speak, or Silent intake, and share only what you want to share."
          actions={
            <LinkButton id="start-help-btn" href="/help" size="lg">
              Get help <ArrowRight aria-hidden="true" />
            </LinkButton>
          }
        />

        <section aria-labelledby="foundation-heading" className="panel">
          <div className="section-header">
            <p className="eyebrow">Your choice matters</p>
            <h2 id="foundation-heading">Designed for difficult moments</h2>
            <p>
              No forced legal fields. No microphone is used by the Speak page. A
              Quick Exit is available throughout the intake flow.
            </p>
          </div>
          <div className="showcase-grid">
            <Card>
              <CardContent className="showcase-stack">
                <ShieldCheck aria-hidden="true" />
                <h3>Private by design</h3>
                <p>
                  Short-lived session state and clear notices help you
                  understand what happens next.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="showcase-stack">
                <ShieldCheck aria-hidden="true" />
                <h3>Human-readable choices</h3>
                <p>
                  Write in your own words, choose quiet prompts, or learn that
                  voice capture is not active yet.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </PublicShell>
  );
}
