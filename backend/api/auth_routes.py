"""auth_routes.py — Auth Blueprint: login, logout, me."""
from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, make_response, request

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/auth/login")
def api_login():
    data     = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    am   = current_app.config["AUTH_MANAGER"]
    user = am.authenticate(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token    = am.create_session(user)
    response = make_response(jsonify({"user": user}))
    response.set_cookie(
        "ff_auth", token,
        httponly=True, samesite="None", secure=True,
        max_age=7 * 24 * 3600,
    )
    return response


@auth_bp.get("/api/auth/logout")
def api_logout():
    token = request.cookies.get("ff_auth")
    if token:
        current_app.config["AUTH_MANAGER"].destroy_session(token)
    response = make_response(jsonify({"ok": True}))
    response.delete_cookie("ff_auth")
    return response


@auth_bp.get("/api/auth/me")
def api_me():
    token = request.cookies.get("ff_auth")
    user  = current_app.config["AUTH_MANAGER"].get_session(token)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": user})
