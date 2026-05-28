# User Journeys

## Journey 0 - UI Lock Before Workflow Rebuild

1. Team opens the app in UI Lock Lab mode.
2. Team reviews Designer Desk, FTC Inbox, and Sticker Agent preview workspaces.
3. Team opens the Design drawer from the topbar.
4. Team switches templates, density, navigation, surface radius, shadows, typography, issue layout, raw-card width, sticker preview mode, and accent color.
5. Browser stores the chosen UI config in localStorage for refresh-safe review.
6. Team copies the final UI config so it can be locked into source tokens before the repo-parity workflow rebuild.

## Journey 1 - Designer To Technical Review

1. Designer opens the dashboard.
2. Designer loads a sample card or uploads a `.txt` cloth card.
3. System parses fabric details and runs deterministic feasibility checks.
4. Designer reviews errors and warnings.
5. Designer uses AI Review to draft communication for missing fields and risks.

## Journey 2 - Technical Approval To Label Output

1. Technical user opens an existing workflow.
2. User reviews gate, construction, GSM, composition, loom, and width concerns.
3. User generates label workbook.
4. User downloads Excel artifact with sticker, technical sheet, and fabric data.

## Journey 3 - Bulk Sticker Generation

1. Designer or documentation user opens Sticker Agent.
2. User selects Bulk Excel mode.
3. User uploads master data Excel with one fabric or roll per row.
4. User optionally uploads a sticker template.
5. System detects label fields in the template and maps them to master columns/computed fields.
6. User generates and downloads a bulk sticker workbook.

## Journey 4 - Buyer File Conversion

1. User uploads a supported `.xlsx` buyer file.
2. System converts comma-in-cell buyer data to a normalized master workbook.
3. User downloads the normalized output.
