# Packet 05R Result — Accessibility Interaction, Language Selector & Form-Recovery Remediation

Status: IMPLEMENTATION COMPLETE — OWNER REVIEW PENDING

Owner Review: PENDING

## Objective

Remediate the Packet 05 accessibility-foundation gaps without redesigning Civic Calm, adding a UI framework, changing the database, or beginning Packet 06 work.

## Packet 05 baseline commits

- Implementation commit: `61b7e373abfd4f8a4d3779d129eead451fdf4de7`
- Implementation CI: `37120152798` — SUCCESS
- Evidence closure: `d955848cebab54526b4154ca2115202b0c1aa6c2`
- Final closure CI for Packet 05: `37120249513` — SUCCESS

## Tooltip focus defect and remediation

The previous Tooltip placed an already-focusable trigger inside a `tabIndex=0` wrapper, creating a duplicate keyboard stop. Tooltip now accepts a single React element, composes its existing `aria-describedby` values with a generated tooltip ID, and leaves focus on the trigger. Keyboard focus and pointer hover reveal the `role="tooltip"` content without replacing the trigger's accessible name.

## Language-selector accessibility defect and remediation

LanguageSelector now implements the editable combobox/listbox relationship: the search input exposes `role="combobox"`, `aria-autocomplete`, `aria-expanded`, `aria-controls`, and a safe `aria-activedescendant`; options have stable IDs, `role="option"`, and `aria-selected`. ArrowUp/ArrowDown, Enter, and Escape are supported. Filtering, language-array changes, selection, and empty results normalize active state so stale descendants cannot remain.

The permanently visible option list and its keyboard behavior are documented in the control help text. Native-script names and RTL preparation remain unchanged.

## Error-summary omission and form recovery

`ErrorSummary` is a reusable client primitive with a plain-language heading, `role="alert"`, focusable programmatic heading, and links to invalid controls. It focuses once when a changed error set appears; repeated renders do not repeatedly steal focus. `focusFirstInvalid` provides a small reusable helper for validation failure flows without embedding domain logic in FormField.

The `/design-system` route includes a clearly synthetic invalid-form example with two invalid fields. Its keyboard path submits the form, focuses the summary, tabs to the first error link, and focuses the corresponding control.

## FormField semantic hardening

FormField now merges consumer-provided `aria-describedby` with generated helper and error IDs without duplicates. Compatible native input, select, and textarea controls receive synchronized `required` and `aria-required` state when FormField is marked required. Unsupported child controls do not receive invalid native props.

## Tabs and dialog regression improvements

Tabs now support Home and End navigation, retain automatic activation, and safely render no tablist when given an empty item array. Native Dialog explicitly focuses its close control on open and continues to restore focus to the trigger on close and Escape.

## Frontend tests and gates

- `npm ci` — passed; no dependency added.
- Prettier format check — passed.
- Shared contracts build — passed.
- Strict TypeScript — passed.
- ESLint — passed.
- Vitest — 3 files, 16/16 tests passed.
- Next.js production build — passed; `/design-system` statically generated.
- Playwright — 11/11 passed, including tooltip single-stop, error-summary link recovery, combobox empty-result safety, dialog initial/return focus, 320px, RTL, reduced motion, smoke, and health scenarios.
- Axe — homepage zero WCAG 2.1 AA violations; design-system route zero serious/critical violations.

## Backend regressions

No backend files, migrations, or Packet 04R security architecture were changed. Existing regression evidence remains green: Ruff, mypy, 50/50 backend tests, PostgreSQL replay, Alembic drift check, 41 core tables, and seven OpenAPI paths.

## Security gates

Existing evidence remains green: Gitleaks, `npm audit`, and `pip-audit`. No new large UI dependency or form framework was added.

## Database and scope boundary

No database change was required. Core table count remains 41. Packet 06 remains `NOT_STARTED`; no channel gateway, consent engine, session policy, citizen intake, voice capture, or AI workflow work was started.

## Final evidence

- Final commit: `5ca9d4979e611e7893ed1c589d78d5a5b370706f`
- Final CI run: `37121220869` — SUCCESS
- Expected branch: `main`
- Expected working tree: clean and synchronized with `origin/main`

## Packet 06 handoff

Stop after final CI verification and owner review. Packet 06 is not authorized by this remediation.
