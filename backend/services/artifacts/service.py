from __future__ import annotations

import re
import uuid
from pathlib import Path


def ensure_artifact_dir(runtime_dir: Path) -> Path:
    path = runtime_dir / "artifacts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_artifact_name(prefix: str, suffix: str) -> str:
    clean_prefix = re.sub(r"[^A-Za-z0-9_.-]+", "_", prefix).strip("._") or "artifact"
    clean_suffix = suffix if suffix.startswith(".") else f".{suffix}"
    return f"{clean_prefix}_{uuid.uuid4().hex[:8]}{clean_suffix}"


def artifact_path(runtime_dir: Path, filename: str) -> Path:
    safe = Path(filename).name
    return ensure_artifact_dir(runtime_dir) / safe
