# Worklog

## 2026-05-28

- Inspected workspace and hackathon PDF context.
- Created `textile-workflow-platform` scaffold.
- Added backend Flask API, SQLite database layer, feasibility service, AI service, artifact service, and sticker service.
- Added frontend Vite/React app with dashboard, fabric check, AI review, label studio, and artifacts views.
- Added sample cloth card and template placeholder.
- Added documentation pack and docs freshness guard.
- Browser verification found and fixed the sample-card endpoint path.
- Fixed docs freshness and gitignore edge cases found after initializing the new repo.
- Browser verification showed reload state loss; recent workflow rows now reopen the workflow.
- Final verification passed: backend tests, frontend build, docs freshness, desktop browser workflow, mobile layout check, and recent-workflow reopen.
- Added bulk sticker generation endpoint and UI with master Excel picker, optional template picker, sheet-name input, mapping preview, row preview, and download.
- Added source card raw/parsed toggle to review flow.
- Browser verified raw card review and Bulk Excel Sticker Agent controls.
- Updated TXT upload handling so selected cloth-card files populate the visible editor, and Review opens every workflow on the exact raw uploaded text.
- Hardened TXT preview loading so a failed browser file read clears the editor instead of leaving stale text.
- Updated Label Studio so single and bulk generation show a direct download button in place instead of sending the user to Artifacts.
- Separated workflow sticker artifacts from bulk sticker artifacts in frontend state.
- Corrected manual text-entry source naming so edited cards no longer appear as the bundled sample file.
- Added UI configuration tokens, localStorage persistence, and a right-side Design Control Drawer.
- Added Designer Desk, FTC Inbox, and Sticker Agent static preview workspaces for UI locking before repo-parity workflow implementation.
- Wired preview navigation above the existing live MVP tools and added live controls for template, density, navigation, radius, shadows, typography, issue layout, raw-card width, sticker preview, and accent color.
- Adjusted the Design drawer opener/scrim handling after browser verification showed the click sequence could immediately close the drawer.
- Fixed the responsive sidebar stack so it does not overlay the topbar Design button in the in-app browser width.
- Added a Copy UI Config fallback behavior so the drawer still shows a copied state while the JSON preview remains visible if clipboard permissions are blocked.
- Audited false feasibility warnings on valid cloth-card uploads and traced the root cause to single-split parsing of multi-column textile card rows.
- Added regression coverage for the clean sample card, sanitized Vardhman-style multi-column cloth-card parsing, engineered repeat/selvedge layouts, and workflow status gating for data-completeness warnings.
- Updated the feasibility parser to extract multiple fields per line, derive card refs from cloth-card headers, split `Gry.EndPik`/`Fin.EndPik`, read warping-section totals, and derive construction from count/EPI/PPI/weave.
- Tuned noisy feasibility rules: grey-width EPI consistency now prefers grey width, cover factor allows the clean demo constructions, theoretical GSM only compares explicit values, selvedge distribution uses selvedge-to-total ratio, and repeat/pattern alignment is informational.
- Refreshed local runtime submissions with the new checker while preserving approved/submitted workflow statuses; the uploaded `SA.0326.0030.txt` rows now show `PASS` with no warnings.
- Compared the combined app against the original Fabric Feasibility MVP and ported the missing corrected-card reupload flow into the Designer Desk.
- Tightened FTC send gating so `WARNING` and `ERROR` cards remain `draft`; designers can only send `PASS` cards to FTC.
- Added browser-visible reupload controls for non-pass editable submissions and refreshed local runtime warning submissions from `ready` to `draft`.
- Investigated refresh logout/user-switch behavior and traced it to `SameSite=None; Secure` cookies on local HTTP plus a shared `ff_auth` cookie name across localhost apps.
- Updated auth routes and decorators to use the app-specific `textile_os_auth` cookie, clear the legacy `ff_auth` cookie on login/logout, and choose local-safe cookie attributes in development.
- Browser-verified that logging in as `designer1` survives a refresh on `http://localhost:5173/` and remains on Designer Desk as `Design Team · designer`.
- Next work: capture polished screenshots and record the demo walkthrough video.
