"""
ftc_routes.py — Designer + FTC + message + public verify blueprints.
All auth failures return JSON (never redirect). Uses the platform's
own check_fabric() service, not the FFC's checker.py.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import uuid

from flask import Blueprint, current_app, g, jsonify, request

from api.auth_decorators import login_required, role_required
from api.utils import extract_text_payload
from db import (
    add_message,
    create_approval,
    create_submission,
    get_approval_by_id,
    get_approval_for_submission,
    get_messages,
    get_submission,
    list_all_submissions_for_ftc,
    list_designer_submissions,
    list_ftc_inbox,
    update_submission_check,
    update_submission_status,
)
from services.feasibility import check_fabric

designer_bp = Blueprint("designer", __name__)
ftc_bp      = Blueprint("ftc",      __name__)
msg_bp      = Blueprint("messages", __name__)
public_bp   = Blueprint("public",   __name__)


def _db():
    return current_app.config["DB_PATH"]


# ── Designer Routes ───────────────────────────────────────────────────────────

@designer_bp.get("/api/designer/submissions")
@role_required("designer", "admin")
def api_designer_list():
    return jsonify(list_designer_submissions(_db(), g.user["user_id"]))


@designer_bp.post("/api/designer/submit")
@role_required("designer", "admin")
def api_designer_submit():
    text, filename = extract_text_payload()
    if not text.strip():
        return jsonify({"error": "No card text provided"}), 400

    result = check_fabric(text, source_filename=filename)
    sub_id = create_submission(
        _db(),
        designer_id   = g.user["user_id"],
        card_ref      = result["card"].get("card_ref") or filename,
        card_filename = filename,
        card_raw_text = text,
        card_parsed   = result["card"],
        check_result  = result["report"],
    )
    sub = get_submission(_db(), sub_id)
    return jsonify({"submission_id": sub_id, "submission": sub}), 201


@designer_bp.post("/api/designer/recheck/<int:sub_id>")
@role_required("designer", "admin")
def api_designer_recheck(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    if sub["designer_id"] != g.user["user_id"] and g.user["role"] != "admin":
        return jsonify({"error": "Access denied"}), 403

    text   = sub["card_raw_text"] or ""
    result = check_fabric(text, source_filename=sub.get("card_filename", "card.txt"))
    new_status = update_submission_check(_db(), sub_id, result["card"], result["report"])
    sub = get_submission(_db(), sub_id)
    return jsonify({"submission": sub, "status": new_status})


@designer_bp.post("/api/designer/send/<int:sub_id>")
@role_required("designer", "admin")
def api_designer_send(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    if sub["designer_id"] != g.user["user_id"] and g.user["role"] != "admin":
        return jsonify({"error": "Access denied"}), 403
    if sub["status"] not in ("ready", "needs_revision"):
        return jsonify({"error": f"Cannot send from status '{sub['status']}'"}), 400

    update_submission_status(_db(), sub_id, "submitted")
    return jsonify({"ok": True, "status": "submitted"})


@designer_bp.get("/api/designer/submissions/<int:sub_id>")
@role_required("designer", "admin")
def api_designer_get(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    if sub["designer_id"] != g.user["user_id"] and g.user["role"] != "admin":
        return jsonify({"error": "Access denied"}), 403
    return jsonify(sub)


# ── FTC Routes ────────────────────────────────────────────────────────────────

@ftc_bp.get("/api/ftc/inbox")
@role_required("ftc_member", "admin")
def api_ftc_inbox():
    status = request.args.get("status")
    rows   = list_ftc_inbox(_db(), status_filter=status)
    return jsonify(rows)


@ftc_bp.get("/api/ftc/inbox/all")
@role_required("ftc_member", "admin")
def api_ftc_all():
    return jsonify(list_all_submissions_for_ftc(_db()))


@ftc_bp.get("/api/ftc/submissions/<int:sub_id>")
@role_required("ftc_member", "admin")
def api_ftc_get(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    approval = get_approval_for_submission(_db(), sub_id)
    sub["approval"] = approval
    return jsonify(sub)


@ftc_bp.post("/api/ftc/feedback/<int:sub_id>")
@role_required("ftc_member", "admin")
def api_ftc_feedback(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404

    data      = request.get_json(silent=True) or {}
    body      = (data.get("body") or "").strip()
    field_ref = data.get("field_ref")
    if not body:
        return jsonify({"error": "Message body required"}), 400

    add_message(_db(), sub_id, g.user["user_id"], g.user["display_name"], g.user["role"], body, field_ref)
    update_submission_status(_db(), sub_id, "needs_revision")
    return jsonify({"ok": True, "status": "needs_revision"})


@ftc_bp.post("/api/ftc/approve/<int:sub_id>")
@role_required("ftc_member", "admin")
def api_ftc_approve(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    if sub["status"] == "approved":
        return jsonify({"error": "Already approved"}), 400
    if sub["status"] != "submitted":
        return jsonify({"error": f"Cannot approve from status '{sub['status']}'"}), 400

    data        = request.get_json(silent=True) or {}
    notes       = data.get("notes", "")
    approval_id = str(uuid.uuid4())
    secret_key  = current_app.config.get("SECRET_KEY", "dev-insecure-key")
    timestamp   = __import__("datetime").datetime.utcnow().isoformat()
    payload     = f"{approval_id}:{sub['card_ref']}:{g.user['user_id']}:{timestamp}"
    signature   = hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    create_approval(
        _db(), sub_id,
        ftc_member_id   = g.user["user_id"],
        ftc_member_name = g.user["display_name"],
        approval_id     = approval_id,
        signature       = signature,
        notes           = notes,
    )
    return jsonify({"ok": True, "approval_id": approval_id})


# ── Messages (any authenticated user) ────────────────────────────────────────

@msg_bp.get("/api/messages/<int:sub_id>")
@login_required
def api_get_messages(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    if (sub["designer_id"] != g.user["user_id"]
            and g.user["role"] not in ("ftc_member", "admin")):
        return jsonify({"error": "Access denied"}), 403
    return jsonify(get_messages(_db(), sub_id))


@msg_bp.post("/api/messages/<int:sub_id>")
@login_required
def api_post_message(sub_id: int):
    sub = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    if (sub["designer_id"] != g.user["user_id"]
            and g.user["role"] not in ("ftc_member", "admin")):
        return jsonify({"error": "Access denied"}), 403

    data      = request.get_json(silent=True) or {}
    body      = (data.get("body") or "").strip()
    field_ref = data.get("field_ref")
    if not body:
        return jsonify({"error": "Body required"}), 400

    msg_id = add_message(_db(), sub_id, g.user["user_id"], g.user["display_name"], g.user["role"], body, field_ref)
    return jsonify({"ok": True, "message_id": msg_id}), 201


# ── Public Routes (no auth) ───────────────────────────────────────────────────

@public_bp.get("/api/verify/<approval_id>")
def api_verify(approval_id: str):
    record = get_approval_by_id(_db(), approval_id)
    if not record:
        return jsonify({"error": "Approval not found"}), 404
    return jsonify(record)


@public_bp.get("/api/submissions/<int:sub_id>/certificate")
def api_certificate(sub_id: int):
    sub      = get_submission(_db(), sub_id)
    if not sub:
        return jsonify({"error": "Not found"}), 404
    approval = get_approval_for_submission(_db(), sub_id)
    return jsonify({"submission": sub, "approval": approval})
