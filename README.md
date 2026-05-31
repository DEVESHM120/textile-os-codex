# Textile OS — Fabric Feasibility & Workflow Platform

> End-to-end automation for fabric feasibility checking, FTC approval workflows,
> and production-ready label generation — built for textile mills, exporters,
> and fashion sourcing teams.

**Live Demo:** https://textile-os-codex.vercel.app

| Login | Username | Password |
|-------|----------|----------|
| Designer | `designer1` | `designer123` |
| FTC Reviewer | `ftc1` | `ftcmember123` |

**Demo files (cloth cards + master Excel):** [demo/](demo/)

---

## The Problem

In a textile mill or export house, every new fabric design goes through a manual
feasibility check before it reaches the loom. A designer fills out a cloth card —
a dense technical document listing loom parameters, yarn counts, reed specs,
GSM targets, warp/weft construction, weave plans, and composition percentages.

That card is then physically or digitally passed to a **Fabric Technical Committee
(FTC)** reviewer, who manually cross-checks it against SOPs: Does the reed count
match EPI? Is the GSM realistic for this yarn count and construction? Are the
selvedge ends within loom capacity? Is the composition declaration consistent
with yarn details?

This process today is:
- **Manual and repetitive** — the same 20+ checks run by eye every time
- **Prone to errors** — handwritten or loosely formatted cards miss fields
- **Slow to iterate** — a card bounces between designer and reviewer multiple
  times before approval
- **Untracked** — no audit trail of who approved what, when, and why

The same data is then re-entered by hand into Excel to print production labels
and stickers for mill dispatch. Any mismatch between the approved spec and the
label creates a costly rework.

---

## The Solution

**Textile OS** digitizes and automates the entire pre-production fabric workflow:

### 1. Intelligent Cloth Card Parser
Upload a standard industry `.txt` cloth card. The platform extracts **60+
fields** — EPI, PPI, GSM, reed count, warp/weft yarn counts, composition,
selvedge ends, weave repeat data, loom type, and more — handling the flexible
fixed-width formats mills actually use, with 40+ field-name aliases (e.g.,
"Gry.EndPik", "Grey EPI", "greige epi" all map to the same field).

### 2. Deterministic Feasibility Rule Engine
22 SOP-style rules run instantly against the parsed card:
- **Structural checks** — ends/dents/harness count consistency, warp balance
- **Loom capacity checks** — beam weight, reed load, pick rate within machine limits
- **Yarn checks** — composition percentage totals, warp/weft count ranges
- **Weight checks** — GSM vs. yarn count plausibility, fabric category match
- **Weave checks** — repeat limits, shaft count, drawing consistency

Every check returns a **PASS / WARNING / ERROR** with a specific code and
actionable message — no ambiguity, no interpretation needed.

### 3. AI-Assisted Communication Layer
An AI layer (OpenAI GPT-4o-mini) reads the rule results and generates:
- A plain-English **risk summary** for non-technical stakeholders
- **Correction suggestions** — up to 6 specific actions to fix errors
- **Label copy** — marketing-friendly fabric description for buyer-facing materials
- **Technical sheet text** — mill communication notes for sampling

The AI never overrides rule gates. Deterministic checks are the source of truth.

### 4. FTC Review & Approval Workflow
Designers submit checked cards to the FTC queue. Reviewers can:
- Toggle between raw card text and a **normalized parsed-fields table**
- Click any spec field to **tag it in a comment** (e.g. "GSM — confirmed against
  lab sample")
- Approve or send back with revision notes
- Each approval generates a **signed certificate** with a public verification URL

### 5. Production Label & Sticker Generator
Approved fabric data is transformed into a formatted Excel workbook with three
sheets — a print-ready **sticker sheet**, a **technical sheet** for mill sampling
communication, and a **fabric data sheet** for records. Supports bulk generation
from a supplier master list (`.xls`/`.xlsx`).

---

## Who This Is For

| Segment | Pain Point Solved |
|---------|------------------|
| **Textile mills** | Automate in-house feasibility review; eliminate manual SOP cross-checks |
| **Fabric exporters** | Speed up buyer approval cycles; generate professional label artifacts |
| **Fashion sourcing teams** | Standardize how supplier cards are evaluated across multiple vendors |
| **Product development teams** | Create a traceable audit trail from design spec to approved fabric |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Lucide React |
| Backend | Python, Flask 3, SQLite (WAL mode) |
| AI | OpenAI GPT-4o-mini (optional — falls back gracefully) |
| Excel I/O | openpyxl, xlrd |
| Auth | HMAC-SHA256 session tokens, role-based access |
| Hosting | Vercel (frontend) · Render (backend) |

---

## Features at a Glance

- Upload real industry cloth cards (`.txt`) — no reformatting needed
- 22-rule deterministic feasibility engine with PASS / WARNING / ERROR gates
- AI-generated risk summaries and label copy
- Designer → FTC approval workflow with field-level commenting
- Printable approval certificate with public verification link
- File attachments on submissions (images, PDFs)
- Single-card and bulk sticker/label Excel generation
- Role-based access: Designer, FTC Member, Admin

---

## Try It With Demo Data

Download files from the [demo/](demo/) folder:

**Cloth cards (upload in Designer Desk):**
- `demo/cloth-cards/SA.0326.0030.txt` — clean 100% Cotton dobby card (happy path)
- `demo/cloth-cards/SA.0226.0024-errors-demo.txt` — card with data issues (shows error detection)

**Master Excel (upload in Sticker Agent → Bulk Sticker Generation):**
- `demo/NPG Men Rupeshwar.xls` — real NPG menswear master fabric list

Full step-by-step walkthrough: [demo/README.md](demo/README.md)

---

## Local Setup

```bash
# Clone and install
git clone https://github.com/DEVESHM120/textile-os-codex.git
cd textile-os-codex/textile-workflow-platform

# Backend
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && npm run dev
# In a second terminal:
cd .. && .venv/Scripts/python backend/app.py
```

Default URLs: Frontend `http://localhost:5173` · API `http://localhost:5005`

Copy `.env.example` to `.env` and add your `OPENAI_API_KEY` to enable AI summaries
(the app works without it — AI features degrade gracefully to rule-based text).
