# Packet 05 Component Inventory

Status values: `LIVE` means implemented reusable primitive; it does not mean a product workflow is live.

| Component | Status | Purpose / variants | Accessibility semantics | Future consumers | Tests |
| --- | --- | --- | --- | --- | --- |
| Button / LinkButton | LIVE | Primary, secondary, tertiary, danger, quiet; sm/md/lg; loading/disabled | Native button/link, visible focus, stable loading label and width | All surfaces | Unit, keyboard, Axe |
| IconButton | LIVE | Accessible compact actions | Required accessible label; decorative child hidden | Toolbars and panels | Unit/API, Axe |
| Input / Textarea / Select | LIVE | Standard text and selection controls | Native controls, 44px target, invalid state | Intake and operator forms | Unit, keyboard, Axe |
| Checkbox / RadioGroup | LIVE | Choice primitives | Native inputs, fieldset/legend, visible text | Consent and preferences | Keyboard, Axe |
| Label / HelperText / FieldError / FormField / ErrorSummary | LIVE | Predictable field composition and invalid-form recovery | Merged consumer/helper/error descriptors, synchronized required state, focused summary, field links, and first-invalid helper | Every form | Unit, keyboard, Axe |
| Card / Panel / Surface / Divider | LIVE | Moderate civic surface hierarchy | Semantic article/section where applicable | All shells | Showcase/Axe |
| Badge / StatusBadge | LIVE | Neutral/semantic and truth-state labels | Text plus icon; never color-only | Capability and workflow status | Unit, Axe |
| Alert / InlineNotice | LIVE | Info, success, warning, danger | Status/alert role based on urgency | Inline guidance and validation | Axe |
| Tooltip / Popover | LIVE | Supplementary help and disclosure | Tooltip composes `aria-describedby` onto the single trigger; keyboard and pointer available | Dense operator help | Unit, keyboard, Axe |
| Dialog | LIVE | Consequential confirmation | Native dialog, Escape, specific actions, focus restoration | High-impact actions | Unit, Playwright |
| Tabs | LIVE | Composable content grouping | Tab/list/panel roles; arrow/Home/End movement; safe empty state | Operator and institutional views | Unit, keyboard, Axe |
| Progress / Spinner / Skeleton | LIVE | Determinate, compact indeterminate, structural loading | Native progress/status; nonessential animation removed for reduced motion | Async workflows | Reduced-motion E2E |
| Breadcrumb | LIVE | Hierarchical orientation | Named nav and current page | Institutional hierarchy | Axe |
| EmptyState / ErrorState | LIVE | Safe next action, retry/navigation, optional reference ID | Human-readable text; no stack/error internals | All workflows | Showcase/Axe |
| DegradedNotice / ConnectionStatus | LIVE | Explain partial availability and what still works | Persistent status text plus icon | Offline/realtime workflows | Showcase/Axe |
| PageHeader / SectionHeader | LIVE | Consistent hierarchy and action placement | Heading structure and bounded explanatory copy | Every page | Axe |
| LanguageSelector | LIVE | Native name, English reference, filter, selected state | Editable combobox/listbox relationship with stable options and `aria-activedescendant` | Multilingual shells | Unit, Playwright, RTL |
| SkipLink / VisuallyHidden / LiveRegion | LIVE | Navigation and assistive announcements | Focusable skip target, visually-hidden text, polite/assertive regions | All shells/features | Playwright, Axe |
| PublicShell / CitizenShell | LIVE | Mobile-first public landmarks and low density | Skip link, header, main, footer | Packets 07 and public routes | Mobile/Axe |
| OperatorShell / InstitutionalShell | LIVE | Moderate desktop structure and optional aside | Named navigation/main/aside landmarks | Packets 13, 17, 21, 24 | Responsive showcase |
| ImmediateSafety | LIVE | Five read-only safety states | Dimension, state, icon/shape, explanation | Human triage surfaces | Showcase/Axe |
| SviStateCard | LIVE | LOW/MODERATE/HIGH/CRITICAL qualitative bands | Explicit non-diagnostic explanation | Packet 11/13 | Showcase/Axe |
| IncidentUrgency | LIVE | ROUTINE/PRIORITY/URGENT/CRITICAL | Independent dimension and factual explanation | Packet 09/13 | Showcase/Axe |
| Uncertainty | LIVE | Seven normal uncertainty conditions | Persistent explanatory status | AI review surfaces | Showcase/Axe |
| EvidenceChip / ProvenanceChip | LIVE | Source, modality, confidence, quality, human review | Textual provenance and secondary confidence | Evidence inspector and handoff | Showcase/Axe |
| HumanReviewStatus | LIVE | Suggestion, review, confirmation, modification, dismissal, escalation | Text and distinct factual icon | Operator oversight | Showcase/Axe |

Public exports flow from `src/components/index.ts` through category indexes. Feature code should import the public API rather than private deep paths.
