from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REQUIRED_DOCS = {
    "docs/DECISIONS.md",
    "docs/WORKLOG.md",
    "docs/VALIDATION_NOTES.md",
    ".agent/tasks/task.md",
}

SOURCE_PREFIXES = ("backend/", "frontend/", "scripts/", "data/")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "-uall"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Docs freshness check skipped: git status is unavailable.")
        return 0

    changed = {
        line[3:].replace("\\", "/")
        for line in result.stdout.splitlines()
        if len(line) > 3
    }
    source_changed = any(path.startswith(SOURCE_PREFIXES) for path in changed)
    docs_changed = REQUIRED_DOCS.issubset(changed) or not changed

    if source_changed and not docs_changed:
        print("Source changed without all required planning docs updated.")
        print("Required docs:")
        for doc in sorted(REQUIRED_DOCS):
            marker = "updated" if doc in changed else "missing"
            print(f"  - {doc}: {marker}")
        return 1

    print("Docs freshness check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
