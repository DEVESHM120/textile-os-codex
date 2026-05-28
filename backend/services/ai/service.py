from __future__ import annotations

import json
import os
from typing import Any


SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "missing_fields": {"type": "array", "items": {"type": "string"}},
        "risk_summary": {"type": "string"},
        "correction_suggestions": {"type": "array", "items": {"type": "string"}},
        "label_copy": {"type": "string"},
        "technical_sheet_text": {"type": "string"},
    },
    "required": [
        "missing_fields",
        "risk_summary",
        "correction_suggestions",
        "label_copy",
        "technical_sheet_text",
    ],
}


def build_ai_summary(workflow: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_summary(workflow, reason="OPENAI_API_KEY is not configured.")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a textile product development assistant. "
                        "Return JSON that follows the schema. Do not change the deterministic gate."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "fabric": workflow.get("fabric", {}).get("parsed", {}),
                            "feasibility_report": workflow.get("feasibility_report", {}),
                        }
                    ),
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "textile_workflow_summary",
                    "strict": True,
                    "schema": SUMMARY_SCHEMA,
                }
            },
        )
        content = getattr(response, "output_text", "") or _extract_response_text(response)
        parsed = json.loads(content)
        parsed["source"] = "openai"
        return parsed
    except Exception as exc:
        return _fallback_summary(workflow, reason=f"OpenAI summary failed: {exc}")


def _extract_response_text(response: Any) -> str:
    chunks = []
    for output in getattr(response, "output", []) or []:
        for content in getattr(output, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)
    return "".join(chunks)


def _fallback_summary(workflow: dict[str, Any], *, reason: str) -> dict[str, Any]:
    card = workflow.get("fabric", {}).get("parsed", {})
    report = workflow.get("feasibility_report", {})
    issues = report.get("errors", []) + report.get("warnings", [])
    missing_fields = sorted(
        {
            issue.get("details", {}).get("field", "")
            for issue in issues
            if issue.get("code") in {"MISSING_REQUIRED_FIELD", "WEAVE_NUMBER_MISSING", "REED_MISSING"}
            and issue.get("details", {}).get("field")
        }
    )
    top_issues = [issue.get("message", "") for issue in issues[:4] if issue.get("message")]
    gate = report.get("gate", "UNKNOWN")
    risk_summary = (
        f"Gate is {gate}. "
        + ("Key review points: " + " ".join(top_issues) if top_issues else "No major feasibility blockers were detected.")
    )
    corrections = [
        issue.get("details", {}).get("action") or issue.get("message")
        for issue in issues[:6]
        if issue.get("details", {}).get("action") or issue.get("message")
    ]
    composition = card.get("composition", "composition pending")
    construction = card.get("construction", "construction pending")
    label_copy = f"{composition} fabric, {construction}, checked through textile workflow gate {gate}."
    technical_sheet_text = (
        f"Use this record for sampling communication. Verify {card.get('card_ref', 'the card')} "
        f"against mill SOPs before release. {reason}"
    )
    return {
        "missing_fields": missing_fields,
        "risk_summary": risk_summary,
        "correction_suggestions": corrections,
        "label_copy": label_copy,
        "technical_sheet_text": technical_sheet_text,
        "source": "fallback",
        "fallback_reason": reason,
    }
