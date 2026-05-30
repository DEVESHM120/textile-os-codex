# Task Tracker

Updated: 2026-05-31

## Done

- Created combined project scaffold.
- Added Flask API skeleton and runtime SQLite database.
- Added feasibility parser and 22 deterministic rule checks.
- Added AI summary service with OpenAI path and fallback path.
- Added sticker/label Excel artifact generator.
- Added React dashboard, fabric check, AI review, label studio, and artifacts views.
- Added sanitized sample cloth card.
- Added docs pack and docs freshness guard.
- Fixed sample-card API path found during browser verification and added regression coverage.
- Fixed docs freshness and gitignore issues found after repo initialization.
- Made recent workflow rows reopen full workflow records after reload.
- Added raw/parsed source card visibility to feasibility review.
- Added bulk Sticker Agent mode with master Excel, optional template, mapping preview, and bulk output download.
- Made uploaded TXT cloth-card content visible in the editor and default feasibility review to Raw TXT.
- Hardened TXT preview loading to avoid stale editor text if the browser cannot read a selected file.
- Added direct Sticker Agent download buttons after workflow and bulk sticker generation.
- Kept workflow and bulk sticker download state separate in Label Studio.
- Corrected manual edited card source naming to `manual-entry.txt`.
- Added UI lock configuration layer with browser localStorage persistence.
- Added Design Control Drawer for live template, density, navigation, surface, issue, raw-card, sticker-preview, and accent tuning.
- Added static Designer Desk, FTC Inbox, and Sticker Agent preview workspaces.
- Adjusted Design drawer pointer handling so opening from the topbar works reliably during browser review.
- Fixed responsive nav stacking so the preview sidebar does not cover the Design control at in-app browser widths.
- Added Copy UI Config fallback state while keeping the JSON config visible in the drawer.
- Fixed false feasibility warnings for valid cloth-card uploads.
- Added multi-column textile cloth-card parser coverage and implementation for Vardhman-style labels, compound EndPik fields, raw header card refs, and warping-section totals.
- Tuned feasibility rules so clean sample cards and internally consistent engineered repeat layouts do not produce warning gates.
- Added workflow status coverage so data-completeness parser warnings stay in `draft` instead of becoming `ready`.
- Refreshed local runtime submissions with the new checker while preserving approved/submitted states.
- Browser-verified Designer Desk now shows the reprocessed `SA.0326.0030` card as `PASS`, `0E · 0W`, with no Warnings section in the opened detail view.
- Compared the combined app with the original Fabric Feasibility MVP and ported the missing corrected-card reupload workflow.
- Tightened Designer Desk/FTC gating so only `PASS` cards can be marked `ready` and sent to FTC; `WARNING` and `ERROR` cards remain editable drafts.
- Added tests and UI for reuploading a corrected `.txt` into the same submission, then moving it to `ready` after the corrected card passes.
- Browser-verified warning cards show `Draft`, disabled `Send to FTC`, and visible `Re-upload Corrected Card` action.

## In Progress

- Capture polished screenshots and demo video.

## Next

- Add screenshots and demo walkthrough notes after browser verification.
- Add deployment notes after local demo is stable.
