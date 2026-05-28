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
- Next work: capture polished screenshots and record the demo walkthrough video.
