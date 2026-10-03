import {
  Bell,
  Check,
  ExternalLink,
  FlaskConical,
  Info,
  MoreHorizontal,
} from "lucide-react";
import {
  Alert,
  Badge,
  Breadcrumb,
  Button,
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  Checkbox,
  ConnectionStatus,
  DegradedNotice,
  Dialog,
  Divider,
  EmptyState,
  ErrorState,
  EvidenceChip,
  ErrorRecoveryDemo,
  FormField,
  HumanReviewStatus,
  IconButton,
  ImmediateSafety,
  IncidentUrgency,
  InlineNotice,
  Input,
  InstitutionalShell,
  LanguageSelector,
  LinkButton,
  LiveRegion,
  PageHeader,
  Panel,
  Popover,
  Progress,
  ProvenanceChip,
  RadioGroup,
  SectionHeader,
  Select,
  Skeleton,
  Spinner,
  StatusBadge,
  Surface,
  SviStateCard,
  Tabs,
  Textarea,
  Tooltip,
  Uncertainty,
} from "@/components";

const swatches = [
  ["Background", "var(--background)", "--background"],
  ["Surface", "var(--surface)", "--surface"],
  ["Foreground", "var(--foreground)", "--foreground"],
  ["Primary", "var(--primary)", "--primary"],
  ["Information", "var(--info)", "--info"],
  ["Success", "var(--success)", "--success"],
  ["Warning", "var(--warning)", "--warning"],
  ["Danger", "var(--danger)", "--danger"],
] as const;

const truthStates = [
  "FOUNDATION_READY",
  "NOT_STARTED",
  "BASELINE_CANDIDATE",
  "PROVISIONAL",
  "SANDBOX",
  "ADAPTER_READY",
  "LIVE",
  "DEGRADED",
] as const;

export default function DesignSystemPage() {
  return (
    <InstitutionalShell>
      <div className="showcase">
        <div className="synthetic-banner">
          <FlaskConical aria-hidden="true" /> SYNTHETIC_DEMO · Engineering
          verification surface · No live citizen data or capability
        </div>
        <Breadcrumb
          items={[
            { label: "Foundation", href: "/" },
            { label: "Design system" },
          ]}
        />
        <PageHeader
          eyebrow="Packet 05 · Internal showcase"
          title="Civic Calm design system"
          description="A production-oriented visual and interaction foundation: warm, restrained, truthful, keyboard-operable, and prepared for multilingual public-service workflows."
          actions={
            <LinkButton href="/" variant="secondary">
              Foundation overview
            </LinkButton>
          }
        />

        <section
          id="foundations"
          className="showcase-section"
          aria-labelledby="foundations-heading"
        >
          <SectionHeader
            title="Foundations"
            description="Semantic tokens separate intent from raw values. Color is always reinforced by text and shape."
          />
          <Panel>
            <h2 id="foundations-heading" className="visually-hidden">
              Foundations and colors
            </h2>
            <div className="showcase-grid">
              {swatches.map(([label, value, token]) => (
                <div className="token-swatch" key={token}>
                  <span
                    className="token-swatch__color"
                    style={{ "--swatch": value } as React.CSSProperties}
                    aria-hidden="true"
                  />
                  <span>
                    <strong>{label}</strong>
                    <br />
                    <code>{token}</code>
                  </span>
                </div>
              ))}
            </div>
          </Panel>
        </section>

        <section id="typography" className="showcase-section">
          <SectionHeader
            title="Typography"
            description="A readable system stack with explicit Indic-script fallbacks. Linguistic validation remains pending."
          />
          <Surface>
            <p className="type-sample type-sample--display">
              Calm enough to understand
            </p>
            <h2 className="type-sample">
              Clear hierarchy for consequential information
            </h2>
            <p className="type-sample type-sample--body">
              Long-form citizen guidance stays near 60–75 characters per line,
              uses a 16px minimum body size, and avoids compressed legal or
              technical language.
            </p>
            <p className="type-sample">
              हिन्दी · বাংলা · ગુજરાતી · ਪੰਜਾਬੀ · தமிழ் · తెలుగు · ಕನ್ನಡ ·
              മലയാളം · ଓଡ଼ିଆ · اردو
            </p>
          </Surface>
        </section>

        <section id="buttons" className="showcase-section">
          <SectionHeader
            title="Buttons and actions"
            description="Semantic variants, stable loading width, generous targets, and one coherent Lucide icon family."
          />
          <Panel className="showcase-stack">
            <div className="showcase-row">
              <Button>Continue</Button>
              <Button variant="secondary">Review details</Button>
              <Button variant="tertiary">Save draft</Button>
              <Button variant="danger">Delete synthetic item</Button>
              <Button variant="quiet">Cancel</Button>
            </div>
            <div className="showcase-row">
              <Button size="sm">Small</Button>
              <Button size="md">Medium</Button>
              <Button size="lg">Large</Button>
              <Button loading>Saving draft</Button>
              <Button disabled>Unavailable</Button>
              <IconButton label="View notifications">
                <Bell />
              </IconButton>
              <LinkButton href="#forms" variant="secondary">
                Go to forms <ExternalLink aria-hidden="true" />
              </LinkButton>
            </div>
          </Panel>
        </section>

        <section id="forms" className="showcase-section">
          <SectionHeader
            title="Forms"
            description="Labels, helper text, errors, and required state are predictably associated without relying on placeholders."
          />
          <Panel>
            <form className="showcase-stack" action="#forms">
              <FormField
                label="Synthetic reference"
                helperText="Use a non-identifying example label."
                required
              >
                <Input name="reference" defaultValue="DEMO-CASE-05" />
              </FormField>
              <FormField
                label="Contact preference"
                error="Choose how a future service may contact the person."
              >
                <Select name="contact" defaultValue="">
                  <option value="" disabled>
                    Select an option
                  </option>
                  <option>Do not contact</option>
                  <option>Ask before contact</option>
                </Select>
              </FormField>
              <FormField
                label="Additional context"
                helperText="Do not enter real complaint information on this showcase."
              >
                <Textarea
                  name="context"
                  defaultValue="Synthetic demonstration text only."
                />
              </FormField>
              <Checkbox
                label="I understand this is a synthetic engineering fixture."
                defaultChecked
              />
              <RadioGroup
                legend="Example pace preference"
                name="pace"
                options={[
                  {
                    value: "steady",
                    label: "Steady",
                    description: "One clear step at a time.",
                  },
                  {
                    value: "compact",
                    label: "Compact",
                    description: "Show related controls together.",
                  },
                ]}
              />
              <div>
                <Button type="submit">Validate synthetic form</Button>
              </div>
            </form>
          </Panel>
        </section>

        <section id="error-recovery" className="showcase-section">
          <SectionHeader
            title="Error recovery"
            description="A focused summary and field links give keyboard users a clear recovery path after a failed synthetic submission."
          />
          <ErrorRecoveryDemo />
        </section>

        <section id="feedback" className="showcase-section">
          <SectionHeader
            title="Feedback and overlays"
            description="Routine guidance stays inline. Dialogs interrupt only for consequential confirmation."
          />
          <div className="showcase-stack">
            <Alert title="Information available" tone="info">
              This message explains a stable state and remains visible.
            </Alert>
            <InlineNotice title="Saved for human review" tone="success">
              The synthetic draft is available to continue.
            </InlineNotice>
            <DegradedNotice />
            <div className="showcase-row">
              <Tooltip label="A tooltip complements the visible control label.">
                <Button variant="tertiary">
                  <Info aria-hidden="true" /> More context
                </Button>
              </Tooltip>
              <Popover label="View provenance guidance">
                <p>
                  Provenance labels describe where information came from and
                  whether a human reviewed it.
                </p>
              </Popover>
              <Dialog
                triggerLabel="Remove example"
                title="Remove this synthetic example?"
                description="This action removes only the local demonstration item. It does not affect citizen or case information."
              />
            </div>
            <Tabs
              label="Example information groups"
              items={[
                {
                  id: "summary",
                  label: "Summary",
                  content: (
                    <p>Concise information required for the current task.</p>
                  ),
                },
                {
                  id: "provenance",
                  label: "Provenance",
                  content: (
                    <p>
                      Source and human-review state remain available without
                      novelty styling.
                    </p>
                  ),
                },
              ]}
            />
          </div>
        </section>

        <section id="statuses" className="showcase-section">
          <SectionHeader
            title="Statuses"
            description="Truth states prevent prototypes, adapters, and candidates from being presented as live capabilities."
          />
          <Panel className="showcase-stack">
            <div className="showcase-row">
              {truthStates.map((status) => (
                <StatusBadge key={status} status={status} />
              ))}
            </div>
            <Divider />
            <div className="showcase-grid">
              <ConnectionStatus state="CONNECTED" />
              <ConnectionStatus state="RECONNECTING" />
              <ConnectionStatus state="OFFLINE" />
              <ConnectionStatus state="DEGRADED" />
            </div>
            <div className="showcase-row">
              <HumanReviewStatus state="AI SUGGESTION" />
              <HumanReviewStatus state="AWAITING REVIEW" />
              <HumanReviewStatus state="HUMAN CONFIRMED" />
              <HumanReviewStatus state="HUMAN MODIFIED" />
            </div>
          </Panel>
        </section>

        <section id="assessment-states" className="showcase-section">
          <SectionHeader
            title="Assessment states"
            description="Immediate safety, stress vulnerability, and reported incident urgency remain independent. All examples are static and synthetic."
          />
          <div className="showcase-grid">
            <ImmediateSafety state="NO_IMMEDIATE_SIGNAL" />
            <SviStateCard state="HIGH" />
            <IncidentUrgency state="URGENT" />
          </div>
          <div
            className="showcase-stack"
            style={{ marginTop: "var(--space-4)" }}
          >
            <Uncertainty state="LANGUAGE_UNCERTAIN" />
            <Uncertainty state="HUMAN_REVIEW_REQUIRED" />
          </div>
        </section>

        <section id="evidence" className="showcase-section">
          <SectionHeader
            title="Evidence and provenance"
            description="Compact factual metadata distinguishes reported, machine-derived, and human-confirmed information."
          />
          <Panel className="showcase-stack">
            <EvidenceChip
              signal="Synthetic temporal phrase"
              modality="TEXT"
              source="SYNTHETIC_DEMO"
              confidence="Moderate"
              quality="Clear fixture"
            />
            <div className="showcase-row">
              <ProvenanceChip value="COMPLAINANT_REPORTED" />
              <ProvenanceChip value="AI_ESTIMATED" />
              <ProvenanceChip value="HUMAN_CONFIRMED" />
              <ProvenanceChip value="NEEDS_VERIFICATION" />
              <ProvenanceChip value="SYNTHETIC_DEMO" />
            </div>
          </Panel>
        </section>

        <section id="loading" className="showcase-section">
          <SectionHeader
            title="Loading"
            description="Use progress for measurable work, a spinner for compact indeterminate work, and skeletons shaped like expected content."
          />
          <Panel className="showcase-stack">
            <Progress value={64} label="Preparing synthetic preview" />
            <div className="showcase-row">
              <Spinner label="Loading synthetic example" />
              <span>Loading supporting metadata</span>
            </div>
            <Skeleton style={{ width: "42%" }} />
            <Skeleton style={{ width: "100%", minHeight: "4rem" }} />
          </Panel>
        </section>

        <section id="errors" className="showcase-section">
          <SectionHeader
            title="Empty and error states"
            description="States explain what happened, what still works, and a safe next action without exposing internals."
          />
          <div className="showcase-grid">
            <EmptyState
              title="No synthetic evidence added"
              description="This is normal for a new demonstration. Add fixtures only when a component needs verification."
              action={
                <Button variant="secondary">Add synthetic fixture</Button>
              }
            />
            <ErrorState
              description="The synthetic preview could not be loaded. Try again later or return to the overview."
              referenceId="DEMO-REF-05"
            />
          </div>
        </section>

        <section id="language-rtl" className="showcase-section">
          <SectionHeader
            title="Language and RTL"
            description="Names appear in their own scripts, flags are never used for languages, and logical CSS supports right-to-left layout."
          />
          <div className="showcase-grid">
            <LanguageSelector />
            <Surface
              className="rtl-example"
              dir="rtl"
              data-testid="rtl-example"
            >
              <Badge tone="info">SYNTHETIC DEMO</Badge>
              <h3>اردو لے آؤٹ کی مثال</h3>
              <p>
                یہ صرف دائیں سے بائیں ترتیب کی تکنیکی جانچ ہے۔ مکمل ترجمہ اور
                لسانی توثیق ابھی باقی ہے۔
              </p>
              <Button variant="secondary">مثال کا بٹن</Button>
            </Surface>
          </div>
        </section>

        <section id="accessibility" className="showcase-section">
          <SectionHeader
            title="Responsive and accessibility foundation"
            description="The same semantic components support 320px layouts, 200% zoom, forced colors, reduced motion, keyboard use, and screen-reader announcements."
          />
          <Panel className="showcase-stack">
            <LiveRegion>
              <Check aria-hidden="true" /> Polite demonstration announcement
              ready.
            </LiveRegion>
            <div className="showcase-row">
              <Badge>320px mobile ready</Badge>
              <Badge>1440px bounded content</Badge>
              <Badge>200% zoom prepared</Badge>
              <Badge>WCAG 2.2 AA target</Badge>
            </div>
            <IconButton label="More accessibility information">
              <MoreHorizontal />
            </IconButton>
          </Panel>
        </section>
      </div>
    </InstitutionalShell>
  );
}
