"""api/utils.py — Shared helpers for blueprint routes."""
from __future__ import annotations

import tempfile
from pathlib import Path

from flask import request
from werkzeug.utils import secure_filename


def extract_text_payload() -> tuple[str, str]:
    """
    Extract cloth card text + filename from the current request.
    Handles both multipart file upload and JSON body.
    Returns (text, filename).
    """
    if request.files.get("file"):
        f        = request.files["file"]
        filename = secure_filename(f.filename or "upload.txt")
        text     = f.read().decode("utf-8", errors="replace")
        return text, filename

    data     = request.get_json(silent=True) or {}
    text     = data.get("text", "")
    filename = data.get("filename", "manual-entry.txt")
    return text, filename
