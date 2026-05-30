"""auth_routes.py — Auth Blueprint: login, logout, me."""
from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, make_response, request

auth_bp = Blueprint("auth", __name__)


def _cookie_name() -> str:
    return current_app.config.get("AUTH_COOKIE_NAME", "textile_os_auth")


def _cookie_kwargs() -> dict:
    return {
        "httponly": True,
        "samesite": current_app.config.get("AUTH_COOKIE_SAMESITE", "Lax"),
        "secure": bool(current_app.config.get("AUTH_COOKIE_SECURE", False)),
    }


def _clear_legacy_auth_cookies(response) -> None:
    for cookie_name in current_app.config.get("LEGACY_AUTH_COOKIE_NAMES", []):
        if cookie_name != _cookie_name():
            response.delete_cookie(cookie_name)


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
        _cookie_name(), token,
        **_cookie_kwargs(),
        max_age=7 * 24 * 3600,
    )
    _clear_legacy_auth_cookies(response)
    return response


@auth_bp.get("/api/auth/logout")
def api_logout():
    token = request.cookies.get(_cookie_name())
    if token:
        current_app.config["AUTH_MANAGER"].destroy_session(token)
    response = make_response(jsonify({"ok": True}))
    response.delete_cookie(
        _cookie_name(),
        samesite=current_app.config.get("AUTH_COOKIE_SAMESITE", "Lax"),
        secure=bool(current_app.config.get("AUTH_COOKIE_SECURE", False)),
    )
    _clear_legacy_auth_cookies(response)
    return response


@auth_bp.get("/api/auth/me")
def api_me():
    token = request.cookies.get(_cookie_name())
    user  = current_app.config["AUTH_MANAGER"].get_session(token)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": user})
