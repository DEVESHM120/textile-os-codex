from __future__ import annotations

from typing import Any

from .parser import parse_cloth_card
from .rules import ALL_RULES, DEFAULT_CONFIG


def check_fabric(
    text: str,
    *,
    source_filename: str = "manual-entry.txt",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    card, parse_issues = parse_cloth_card(text, source_filename)
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    info: list[dict[str, Any]] = []

    for rule_fn in ALL_RULES:
        try:
            result = rule_fn(card, cfg)
        except Exception as exc:
            result = {
                "severity": "INFO",
                "code": "RULE_EXECUTION_ERROR",
                "category": "SYSTEM",
                "message": f"Rule {rule_fn.__name__} raised an unexpected error.",
                "details": {"rule": rule_fn.__name__, "error": str(exc)},
            }
        if not result:
            continue
        _append_by_severity(result, errors, warnings, info)

    for issue in parse_issues:
        _append_by_severity(issue, errors, warnings, info)

    gate = "ERROR" if errors else ("WARNING" if warnings else "PASS")
    return {
        "card": card,
        "report": {
            "gate": gate,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "rules_run": len(ALL_RULES),
            "rules_fired": len(errors) + len(warnings) + len(info),
        },
    }


def _append_by_severity(
    issue: dict[str, Any],
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    info: list[dict[str, Any]],
) -> None:
    severity = issue.get("severity", "INFO")
    if severity == "ERROR":
        errors.append(issue)
    elif severity == "WARNING":
        warnings.append(issue)
    else:
        info.append(issue)
