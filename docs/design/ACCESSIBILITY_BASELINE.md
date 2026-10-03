# Packet 05 Accessibility Baseline

## Target and limits

The engineering baseline targets WCAG 2.2 Level AA and prepares the architecture for a later GIGW audit. Final WCAG certification is `NOT_DONE`; final GIGW audit is `NOT_DONE`. Automated tests do not equal WCAG certification.

## Keyboard policy

- Every interactive primitive must work without a pointer.
- Focus order follows DOM/task order; positive `tabindex` is prohibited.
- Enter/Space use native control behavior; tabs use Left/Right arrows; Escape closes the native dialog.
- Closing a dialog restores focus to its trigger.
- A visible skip link moves directly to the focusable main landmark.

## Focus policy

One high-contrast focus token (`--focus`) produces a 3px ring with separation from the control. It remains visible on warm, muted, primary, and danger surfaces. Browser focus is never removed without a replacement.

## Screen-reader and semantic policy

Use native elements and landmarks first. FormField creates label/help/error relationships. Important persistent errors use alert semantics; ordinary state updates use polite live regions. Decorative icons are `aria-hidden`; icon-only controls require an accessible name. Critical safety or legal information must not be placed only in transient toasts.

## Contrast and color

The semantic palette is tested in rendered Axe runs. Normal text targets 4.5:1, large text 3:1, and component boundaries/focus states appropriate non-text contrast. Status meaning always includes text and an icon/shape; risk color is not a diagnosis or a description of a person.

## Motion

`prefers-reduced-motion` removes nonessential spinner/skeleton animation and reduces transitions to effectively zero. No action, status, or meaning depends on animation. The system includes no autoplay audio, flashing, parallax, countdown, or scroll hijacking.

## Zoom, reflow, and touch

The foundation uses responsive grids, logical properties, wrapping text, and minimum 44px primary targets. Core surfaces are designed for 320px width and 200% browser zoom without loss of essential actions or unintended body-level horizontal scrolling. Desktop content is bounded to preserve readable line lengths.

## RTL and multilingual preparation

Urdu fixtures verify `dir="rtl"` and logical layout. Language names appear in native script and are not represented by flags. The fallback font stack covers major Indic script families, but linguistic and script-level visual validation remains pending.

## Forced colors

Buttons, controls, badges, alerts, assessment states, focus indicators, and loading placeholders include forced-colors behavior. Text, borders, and native controls remain the primary information carriers.

## Automated coverage

- Vitest: loading/disabled button semantics, FormField associations, status labels, language filtering/selection, dialog behavior, and required token contract.
- Playwright: skip link and keyboard path, form entry, language operation, dialog open/Escape/focus restoration, 320×700 overflow, 1440×900 bounds, RTL clipping, and reduced motion.
- Axe: homepage and design-system component groups; zero automated serious/critical violations required.

## Required manual follow-up

Packet 28 must include manual screen-reader testing (NVDA/JAWS/VoiceOver as applicable), 200% and 400% zoom review, Windows High Contrast review, color-vision simulation, Indic-script linguistic QA, cognitive walkthroughs with representative users, and formal WCAG/GIGW conformance assessment.
