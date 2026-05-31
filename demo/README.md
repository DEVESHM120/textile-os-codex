# Demo Data — Textile OS

Use these files to explore the live app at **https://textile-os-codex.vercel.app**

---

## Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Designer | `designer1` | `designer123` |
| FTC Reviewer | `ftc1` | `ftcmember123` |

---

## Cloth Card Files

These are real industry-format cloth cards (Airjet/8C Dobby, 64-shaft peg-plan). The app parses the fixed-width layout — sections like `WARP YARNS`, `PEG-PLAN`, `DRAWING`, `WARPING SECTIONS` — and runs 22 feasibility rules on the extracted data.

| File | What to expect |
|------|----------------|
| [SA.0326.0030.txt](cloth-cards/SA.0326.0030.txt) | 100% Cotton, 20 COM warp × 10 OE weft — clean card, should pass most checks |
| [SA.0226.0024-errors-demo.txt](cloth-cards/SA.0226.0024-errors-demo.txt) | 80%CO/20%PES blend, 10 COM warp — intentionally has data issues to demonstrate how warnings and errors are flagged |

---

## Full Test Walkthrough

### Step 1 — Submit a Cloth Card (Designer login)

1. Log in as `designer1`
2. In **Designer Desk**, click **Upload Card** and select one of the `.txt` files above
3. The app parses the card — extracting EPI, PPI, GSM, reed count, warp/weft counts, total ends, composition, etc. — and runs feasibility rules
4. Review the **Pass / Warning / Error** results  
   - `SA.0326.0030.txt` → mostly green, good card to show the happy path  
   - `SA.0226.0024-errors-demo.txt` → shows how the checker flags issues like count mismatch, composition conflicts
5. Click **Submit for FTC Review**

### Step 2 — FTC Review & Approval (FTC login)

1. Log in as `ftc1` (or open a second browser tab and sign in separately)
2. Go to **FTC Inbox** — the submission appears under "Pending Review"
3. Open the review panel:
   - Toggle **Raw / Parsed Fields** to see the extracted spec table
   - Click any field row to tag it in a comment (e.g. click GSM row → type "GSM confirmed against lab sample")
   - Send the message — it appears in the thread with the field tag
4. Click **Approve** when done

### Step 3 — Print Certificate

After approval, click **Print Certificate** in either the Designer Desk or FTC Inbox to open a printable A4 document with all specs, approval details, and a public verification URL.

### Step 4 — Bulk Sticker Generation (Sticker Agent)

1. Stay logged in, go to the **Sticker Agent** tab
2. Under **Bulk Sticker Generation**, upload [NPG Men Rupeshwar.xls](NPG%20Men%20Rupeshwar.xls)
3. Click **Generate** — the app produces a formatted multi-sticker Excel file ready for production labelling

---

## File Reference

| File | Used In | Description |
|------|---------|-------------|
| `cloth-cards/SA.0326.0030.txt` | Designer Desk | Real dobby cloth card — 100% Cotton, clean data |
| `cloth-cards/SA.0226.0024-errors-demo.txt` | Designer Desk | Same dobby construction, intentional data issues to demo error detection |
| `NPG Men Rupeshwar.xls` | Sticker Agent | Real NPG menswear master fabric list for bulk sticker generation |
