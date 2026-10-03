# SAMBAL Civic Calm Design System

Status: `FOUNDATION_READY`  
Scope: Packet 05 reusable frontend foundation; no citizen, operator, referral, speech, or AI workflow logic.

## Civic Calm philosophy

Civic Calm combines warm public-service clarity, trauma-informed restraint, and modern institutional software. It avoids both cold bureaucratic density and novelty-driven startup styling. Premium quality comes from hierarchy, spacing, typography, predictable behavior, and carefully bounded surfaces—not decoration, gamification, gradients, or AI spectacle.

The interaction principles are choice, predictability, control, privacy, non-judgment, easy correction, easy exit, and low cognitive load. Routine information stays inline. Dialogs are reserved for consequential interruption. Danger styling is reserved for destructive actions.

## Token architecture

Tokens live in `apps/web/src/app/globals.css` in three conceptual layers:

1. Primitive colors provide named raw values.
2. Semantic tokens describe intent (`--background`, `--surface`, `--foreground`, `--primary`, `--info`, `--success`, `--warning`, `--danger`, and risk states).
3. Component rules consume semantic tokens rather than arbitrary colors.

The light theme uses warm ivory backgrounds, deep charcoal text, calm teal actions, muted blue information, subdued amber warning, controlled red danger, and soft green confirmation. Risk colors are never the sole signal and never describe a person. Components add text, icons/shapes, dimension names, and explanatory copy.

## Typography

The system stack starts with a readable Latin sans and provides explicit Noto fallbacks for Devanagari, Bengali, Gujarati, Gurmukhi, Tamil, Telugu, Kannada, Malayalam, Odia, and Urdu. Citizen body copy remains at least 16px and generally stays within 60–75 characters per line. Numerals and compact labels retain adequate size and weight.

Truth state: `TYPOGRAPHIC_SUPPORT_READY`; linguistic and script-by-script visual validation: `PENDING`.

## Spacing, radius, and elevation

- Spacing follows a restrained 4px-derived scale from 4px to 80px.
- Controls use a small radius, cards a moderate radius, and major panels a larger but non-pill radius.
- Borders and surface contrast provide primary separation. A single subtle shadow is available for major panels.
- Citizen shells use comfortable density; operator shells use moderate density. A compact administrative density is not implemented.

## Motion

Motion communicates loading, focus, and state. There is no parallax, ambient movement, bounce, countdown, or scroll hijacking. `prefers-reduced-motion: reduce` removes skeleton/spinner motion and effectively disables nonessential transitions. No information depends on animation.

## Accessibility

The baseline target is WCAG 2.2 AA with later GIGW review preparation. Semantic HTML is preferred over ARIA. The foundation includes skip navigation, landmarks, visible focus, 44px primary targets, label/error/help associations, live regions, keyboard tabs, a focus-restoring native dialog, textual status semantics, forced-colors behavior, and reduced motion.

Automated tests do not equal WCAG certification. Packet 28 owns final WCAG/GIGW audit and manual assistive-technology validation.

## Responsive strategy

Public and citizen shells are mobile-first from 320px. Content grids collapse without turning desktop navigation into a squeezed sidebar. Long text wraps rather than truncates. Desktop content is bounded to 1280px, while citizen prose uses a 72ch maximum. Operator and institutional shells expose different density/layout structures without implementing domain navigation.

## Status and assessment semantics

Truth statuses include `NOT_STARTED`, `FOUNDATION_READY`, `BASELINE_CANDIDATE`, `PROVISIONAL`, `SANDBOX`, `ADAPTER_READY`, `LIVE`, and `DEGRADED`.

The following dimensions remain visually and semantically independent:

- Immediate Safety: current safety-oriented human attention; `NO_IMMEDIATE_SIGNAL` explicitly does not mean safe.
- SVI: qualitative vulnerability/distress triage; not a diagnosis, credibility judgment, or case-worth score.
- Reported Incident Urgency: urgency of reported circumstances independent of emotional presentation.
- Uncertainty: expected evidence-quality or model-boundary information, not a software crash.

## AI and provenance

AI content uses quiet factual labels rather than sparkles, purple gradients, brains, or magic-wand imagery. `AI_ESTIMATED`, `AI_EXTRACTED`, `HUMAN_CONFIRMED`, and other provenance labels communicate source and review status. Human-confirmed content is distinguishable without implying that all machine-assisted content is inherently false.

## Language and RTL

Language controls show names in native scripts with an English reference where useful; flags are prohibited. CSS uses logical properties, and the showcase includes an Urdu `dir="rtl"` fixture. Packet 05 does not claim translated interfaces or linguistic QA.

## Icon and dependency policy

Lucide is the single icon family and was already present before Packet 05. Decorative icons are hidden from assistive technology; icon-only buttons require a `label`. No new npm dependency was added. Native elements and focused local components were sufficient for the foundation.
