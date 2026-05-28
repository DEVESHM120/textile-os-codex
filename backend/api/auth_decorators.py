"""auth_decorators.py — Route protection decorators (JSON-only, no redirects)."""
from __future__ import annotations

from functools import wraps

from flask import current_app, g, jsonify, request


def _get_user():
    token = request.cookies.get("ff_auth")
    return current_app.config["AUTH_MANAGER"].get_session(token)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _get_user()
        if not user:
            return jsonify({"error": "Not authenticated"}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = _get_user()
            if not user:
                return jsonify({"error": "Not authenticated"}), 401
            if user["role"] not in roles:
                return jsonify({"error": "Access denied"}), 403
            g.user = user
            return f(*args, **kwargs)
        return decorated
    return decorator
