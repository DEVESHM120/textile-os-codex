# Validation Notes

## Current Validation Status

Passed for the MVP build.

- Backend tests: `8 passed`.
- Frontend build: `npm run build` passed.
- Docs freshness: passed.
- Browser desktop flow: sample card to feasibility review to AI fallback to label artifact passed.
- Browser mobile layout: dashboard/nav/workflow queue rendered cleanly at mobile width.
- Recent workflow reopen: passed.
- Bulk sticker generation: service/API tests passed; browser verified bulk controls, master/template chooser, sheet input, and output panel.
- Raw card visibility: browser verified raw card and parsed toggle are visible in feasibility review beside issues.
- Raw TXT preservation: API regression coverage now checks that workflow creation stores the exact uploaded/manual raw card text.
- Sticker download UX: browser verified the workflow download button appears in Label Studio; direct API download returned `200` with `.xlsx` MIME type and workbook bytes. The Codex in-app browser cannot save downloaded files itself.
- Manual edited card source naming: browser verified edited cards show `manual-entry.txt` instead of the bundled sample filename.
- UI lock build: frontend build passed after adding UI config tokens, Design Control Drawer, and preview workspaces.
- UI lock backend safety: backend tests remained green after the frontend-only UI lock pass.
- UI lock browser check: verified default Designer Desk preview, drawer opening, template/density/navigation/issue/accent changes, localStorage persistence after refresh, reset to defaults, FTC/Sticker preview navigation, and no horizontal overflow at the in-app browser width.
- Copy UI Config fallback: the visible JSON config remains in the drawer if the in-app browser blocks clipboard writes.

Browser verification found a sample-card API path issue; the route was fixed and a regression test was added.

Docs freshness initially failed because git collapsed untracked directories. The script now uses `-uall`, and the ignore rules were tightened so source artifact services remain visible.

Browser reload showed active workflow state resets to the dashboard queue. Recent workflow rows were made clickable so a user can reopen the saved workflow.

Planned checks:

- `pytest` for backend parser, feasibility rules, sticker generation, and Flask APIs.
- `npm run build` for frontend production build.
- Local browser run through sample card, AI fallback summary, label generation, and artifact download.
- Data hygiene check for ignored runtime files.

## Known MVP Constraints

- AI assistant requires `OPENAI_API_KEY`; fallback summary is used when absent.
- Buyer conversion endpoint supports `.xlsx` in the MVP.
- Reed inventory is demo-configured, not connected to a real mill inventory database.
- Label generation uses a generated workbook format unless a future template mapper is added.
