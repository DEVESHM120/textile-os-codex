# Demo Data — Textile OS

Use these files to explore the live app at **https://textile-os-codex.vercel.app**

---

## Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Designer | `designer1` | `designer123` |
| FTC Reviewer | `ftc1` | `ftcmember123` |

---

## Full Test Walkthrough

### Step 1 — Submit a Fabric Card (Designer login)

1. Log in as `designer1`
2. In **Designer Desk**, click **Upload Card** and select one of:
   - [card-plain-cotton-shirting.txt](cloth-cards/card-plain-cotton-shirting.txt) — 100% cotton plain weave, lightweight shirting
   - [card-dobby-cotton.txt](cloth-cards/card-dobby-cotton.txt) — 100% cotton dobby texture
   - [card-twill-poly-cotton.txt](cloth-cards/card-twill-poly-cotton.txt) — 65/35 poly-cotton workwear twill
   - [card-poplin-stretch.txt](cloth-cards/card-poplin-stretch.txt) — 97/3 cotton-elastane stretch poplin
3. The app parses the card and runs **22 deterministic feasibility rules** (EPI/PPI range checks, GSM vs construction checks, reed count validation, etc.)
4. Review the **Pass / Warning / Error** results
5. Click **Submit for FTC Review** to send to the review queue

### Step 2 — FTC Review & Approval (FTC login)

1. Log in as `ftc1` (or open a second browser tab)
2. Go to **FTC Inbox** — the submission will appear under "Pending Review"
3. Click it to open the review panel:
   - Toggle **Raw / Parsed Fields** to see extracted spec values in a table
   - Click any field row to tag it in a comment (e.g. "GSM looks high for this construction")
   - Type a message and send
4. When satisfied, click **Approve**

### Step 3 — Print Certificate

After approval, click **Print Certificate** in either the Designer Desk or FTC Inbox. This opens a printable A4 certificate with all specs, approval signature, and a verification URL.

### Step 4 — Bulk Sticker Generation (Sticker Agent)

1. Log in as either user, go to the **Sticker Agent** tab
2. Under **Bulk Sticker Generation**, upload [master-fabric-list.xlsx](master-fabric-list.xlsx)
3. Click **Generate** — the app produces a formatted Excel file with one sticker block per fabric row, ready for production labelling

---

## File Reference

| File | Used In | Description |
|------|---------|-------------|
| `cloth-cards/card-plain-cotton-shirting.txt` | Designer Desk | Fine cotton shirting, plain weave |
| `cloth-cards/card-dobby-cotton.txt` | Designer Desk | Cotton dobby with texture weave |
| `cloth-cards/card-twill-poly-cotton.txt` | Designer Desk | Poly-cotton workwear twill |
| `cloth-cards/card-poplin-stretch.txt` | Designer Desk | Stretch poplin with elastane |
| `master-fabric-list.xlsx` | Sticker Agent | 5-row master list for bulk sticker output |
