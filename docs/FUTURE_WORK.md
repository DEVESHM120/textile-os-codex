# Future Work

Items deferred from the MVP sprint (post-1-hour deadline).

## High priority
- **QR print certificates** — `/api/submissions/<id>/certificate` endpoint exists; need a printable React page with embedded QR code (use `qrcode` library)
- **File attachments (B3)** — designer can attach screenshots/images to a submission; drag-drop zone in DesignerDesk, served at `/uploads/<sub_id>/<filename>`
- **Re-upload corrected card** — designer uploads a new .txt for an existing submission (re-run check without creating a new submission)

## Medium priority
- **Data-driven rules from knowledge base** — FFC has `knowledge/rules_approved.json` with 249K-card patterns; import and apply as additional feasibility checks
- **Sticker agent upgrade** — replace the 23-entry `FINISH_LOOKUP` dict in `backend/services/stickers/service.py` with the 4,228-code Excel lookup from `G:\Textile OS\sticker-agent\lookup.py`
- **Admin user management UI** — CRUD for users (role assignment, password reset); backend `AuthManager.list_users()` + `create_user()` already implemented
- **Message notification badge** — nav sidebar badge showing unread FTC message count (backend `count_unread_for_designer()` already in workflow_db.py)

## Low priority / polish
- **Sticker generation from approved submission** — after FTC approval, a "Generate Stickers" button in FTC inbox that calls the existing `/api/workflows/:id/generate-labels` endpoint
- **AI summary in FTC review** — show AI risk summary alongside check results in FtcReview.jsx
- **Approval certificate page** — public `/verify/<id>` page rendered as a printable certificate
- **Deployment notes** — Docker / Waitress setup for production hosting
