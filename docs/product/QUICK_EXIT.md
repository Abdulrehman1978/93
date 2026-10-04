# Quick Exit — Citizen Intake Safety Control

Quick Exit is present throughout citizen intake, including Write, Silent, Speak, policy, and receipt surfaces. It is a visible button and also responds to `Escape`.

On activation the browser clears citizen session state and drafts from `sessionStorage`, then uses `location.replace` to navigate to a neutral, environment-configurable target (`NEXT_PUBLIC_QUICK_EXIT_URL`). Local development and automated tests use the deterministic same-origin `/` fallback. Staging and production builds must set an approved neutral HTTPS destination; the build fails when that value is missing, non-HTTPS, local, or visibly SAMBAL-owned. The operational destination is deployment configuration, not a product claim or legal mandate. The control does not place sensitive state in the URL and the backend public responses send `Referrer-Policy: no-referrer` and `Cache-Control: no-store`.

Quick Exit cannot remove data already transmitted to network infrastructure, browser history created outside the flow, operating-system screenshots, DNS/ISP records, or hostile device monitoring. It is a local safety affordance, not a guarantee of device or network privacy.
