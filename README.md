# Textile Workflow Automation Platform

AI-assisted textile product development workflow for mills, exporters, sourcing teams, and fashion brands.

## Try It Live

**Live app:** https://textile-os-codex.vercel.app

**Demo files + step-by-step guide:** [demo/README.md](demo/README.md)

| Login | Username | Password |
|-------|----------|----------|
| Designer | `designer1` | `designer123` |
| FTC Reviewer | `ftc1` | `ftcmember123` |

Quick test: log in as designer, upload any `.txt` file from [demo/cloth-cards/](demo/cloth-cards/), run the feasibility check, submit for FTC review, then switch to the FTC login and approve it.

The MVP combines:

- Fabric Feasibility Checker: parses cloth-card data and runs deterministic SOP-style checks.
- Sticker and Label Generator: turns the same fabric data into production-ready Excel label artifacts.
- AI Assistant: creates structured missing-data, risk, correction, label-copy, and technical-sheet summaries. The deterministic checker remains the source of truth for PASS, WARNING, and ERROR gates.

## Quick Start

```powershell
cd "G:\codex x outskill\textile-workflow-platform"
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
cd frontend
npm install
npm run build
cd ..
.\.venv\Scripts\python backend\app.py
```

Open the React app in development with:

```powershell
cd "G:\codex x outskill\textile-workflow-platform\frontend"
npm run dev
```

Default URLs:

- Frontend: `http://localhost:5173`
- API: `http://localhost:5005`

## Demo Flow

1. Load or upload a cloth card.
2. Run feasibility checks.
3. Review deterministic risks and AI communication summary.
4. Generate a sticker/label Excel artifact.
5. Download the artifact from the workflow record.

## Agent Rules

Every meaningful code or product change must update:

- `docs/DECISIONS.md`
- `docs/WORKLOG.md`
- `.agent/tasks/task.md`
- `docs/VALIDATION_NOTES.md`

Run:

```powershell
python scripts\check_docs_fresh.py
```

This warns if tracked source changed without the required planning docs changing too.
