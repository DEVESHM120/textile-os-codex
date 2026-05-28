# Decisions Log

## 2026-05-28

- Created a new combined repo instead of modifying either original source repo.
- Chose React + Flask API as requested after planning.
- Kept deterministic rules as the source of truth for PASS, WARNING, and ERROR.
- Added OpenAI Responses API structured output path with fallback summary when no key is configured.
- Stored runtime DB and artifacts under `.runtime`, which is ignored by git.
- Used sanitized demo cloth-card data instead of real Vardhman uploads/outputs.
- Implemented MVP sticker generation as an Excel workbook with Sticker, Technical Sheet, and Fabric Data tabs.
- Limited buyer conversion endpoint to `.xlsx` for the MVP.
- Fixed sample-card API path to resolve from the combined project root.
- Tightened `.gitignore` so source package `backend/services/artifacts` is not hidden by runtime artifact rules.
- Updated docs freshness guard to use `git status --porcelain -uall` so newly scaffolded doc files are detected individually.
- Made recent workflow rows reopen the full workflow after reload.
- Added raw/parsed source-card visibility in feasibility review so users can audit what each issue points to.
- Split Sticker Agent into two modes: generate from checked feasibility workflow and bulk Excel + optional template generation.
- Ported Sticker-Agent template inference behavior: scan template labels, map recognized labels to fields, and fill the cell/value position in bulk output.
- Reset feasibility review to Raw TXT whenever a workflow is opened or checked, and mirror uploaded `.txt` contents into the editor so users can audit exact source text.
- Kept users inside Label Studio after sticker generation and made direct workbook download the primary action for both single-workflow and bulk sticker runs.
- Mark edited text-entry cloth cards as `manual-entry.txt` unless the unchanged sample or an uploaded file is used, so source metadata matches what the user actually checked.
- Kept bulk sticker artifacts separate from workflow sticker artifacts so the two Label Studio modes do not overwrite each other's latest download state.
- Added a UI Lock Lab before the workflow rebuild so design choices can be tuned in-browser before deeper Designer/FTC/Sticker logic is implemented.
- Chose `Mill Ops Console`, `Operator Dense`, and a right-side Design Control Drawer as the default UI direction.
- Added live CSS-variable controls for template, density, navigation, radius, shadow, font scale, table density, issue display, raw-card width, sticker preview, and accent color.
- Stored UI lock settings in browser `localStorage` under `textile-ui-config-v1`; final source-token locking will happen after visual approval.
- Added static preview workspaces for Designer Desk, FTC Inbox, and Sticker Agent so workflow UX can be reviewed before backend workflow rebuild.
