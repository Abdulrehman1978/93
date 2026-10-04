# Quick Exit — Citizen Intake Safety Control

Quick Exit is present throughout citizen intake, including Write, Silent, Speak, policy, and receipt surfaces. It is a visible button and also responds to `Escape`.

On activation the browser clears citizen session state and drafts from `sessionStorage`, then uses `location.replace` to navigate to a neutral, environment-configurable target (`NEXT_PUBLIC_QUICK_EXIT_URL`, default `/`). The control does not place sensitive state in the URL and the backend intake responses send `Referrer-Policy: no-referrer` and `Cache-Control: no-store`.

Quick Exit cannot remove data already transmitted to network infrastructure, browser history created outside the flow, operating-system screenshots, DNS/ISP records, or hostile device monitoring. It is a local safety affordance, not a guarantee of device or network privacy.
