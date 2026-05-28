from __future__ import annotations

import re
from typing import Any


FIELD_ALIASES = {
    "card_ref": ["card ref", "reference", "ref", "ref no", "reference no"],
    "customer": ["customer", "brand"],
    "buyer": ["buyer"],
    "fabric_category": ["fabric category", "category", "fab category"],
    "construction": ["construction", "fabric construction"],
    "composition": ["composition", "fabric composition", "content"],
    "weave": ["weave", "weave structure"],
    "weave_number": ["weave number", "weave no"],
    "loom_type": ["loom type", "loom"],
    "gsm": ["gsm", "finish gsm", "finished gsm"],
    "theoretical_gsm": ["theoretical gsm", "calc gsm", "calculated gsm"],
    "grey_epi": ["grey epi", "greige epi"],
    "finished_epi": ["finished epi", "fin epi"],
    "grey_ppi": ["grey ppi", "greige ppi"],
    "finished_ppi": ["finished ppi", "fin ppi"],
    "grey_width_inches": ["grey width inches", "grey width", "greige width"],
    "finished_width_inches": ["finished width inches", "finished width", "fin width"],
    "reed_count": ["reed count", "reed"],
    "reed_space_inches": ["reed space inches", "reed space"],
    "body_ends": ["body ends"],
    "selvedge_ends": ["selvedge ends", "selvage ends"],
    "total_ends": ["total ends"],
    "ends_per_repeat": ["ends per repeat", "drawing e/r"],
    "peg_plan_repeats": ["peg plan repeats", "peg plan p/r"],
    "shaft_count": ["shaft count", "harness count"],
    "warp_count_ne": ["warp count ne", "warp count"],
    "weft_count_ne": ["weft count ne", "weft count"],
    "warp_weight_percent": ["warp weight percent", "warp weight %"],
    "weft_weight_percent": ["weft weight percent", "weft weight %"],
    "warp_beam_weight_kg": ["warp beam weight kg", "beam weight"],
    "pick_rate_meters_per_min": ["pick rate meters per min", "pick rate", "weft insertion"],
    "finish_code": ["finish code"],
    "k1": ["k1"],
    "k2": ["k2"],
    "k3": ["k3"],
    "k4": ["k4"],
    "k5": ["k5"],
    "k6": ["k6"],
    "k7": ["k7"],
    "k8": ["k8"],
    "k9": ["k9"],
}

REQUIRED_FIELDS = [
    "card_ref",
    "construction",
    "composition",
    "weave",
    "gsm",
    "grey_epi",
    "grey_ppi",
    "finished_width_inches",
    "total_ends",
]

NUMERIC_FIELDS = {
    "gsm",
    "theoretical_gsm",
    "grey_epi",
    "finished_epi",
    "grey_ppi",
    "finished_ppi",
    "grey_width_inches",
    "finished_width_inches",
    "reed_count",
    "reed_space_inches",
    "body_ends",
    "selvedge_ends",
    "total_ends",
    "ends_per_repeat",
    "peg_plan_repeats",
    "shaft_count",
    "warp_count_ne",
    "weft_count_ne",
    "warp_weight_percent",
    "weft_weight_percent",
    "warp_beam_weight_kg",
    "pick_rate_meters_per_min",
}


def _normalize_key(key: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", key.lower()).strip()
    for canonical, aliases in FIELD_ALIASES.items():
        if normalized in aliases:
            return canonical
    return normalized.replace(" ", "_")


def _to_number(value: str) -> float | str:
    clean = str(value).strip()
    match = re.search(r"-?\d+(?:\.\d+)?", clean.replace(",", ""))
    if not match:
        return clean
    try:
        return float(match.group(0))
    except ValueError:
        return clean


def parse_cloth_card(text: str, source_filename: str = "manual-entry.txt") -> tuple[dict[str, Any], list[dict[str, Any]]]:
    card: dict[str, Any] = {"source_filename": source_filename}
    issues: list[dict[str, Any]] = []

    for line in text.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        if ":" in raw:
            key, value = raw.split(":", 1)
        elif "=" in raw:
            key, value = raw.split("=", 1)
        else:
            continue
        canonical = _normalize_key(key)
        value = value.strip()
        if canonical in NUMERIC_FIELDS:
            card[canonical] = _to_number(value)
        else:
            card[canonical] = value

    if "card_ref" not in card:
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
        if first_line and ":" not in first_line and "=" not in first_line:
            card["card_ref"] = re.sub(r"\s+", "-", first_line.upper())[:40]

    _derive_missing_fields(card)

    for field in REQUIRED_FIELDS:
        if card.get(field) in (None, ""):
            issues.append(
                {
                    "severity": "WARNING",
                    "code": "MISSING_REQUIRED_FIELD",
                    "category": "DATA_COMPLETENESS",
                    "message": f"Missing required fabric field: {field.replace('_', ' ')}.",
                    "details": {"field": field, "action": "Add this value before sampling approval."},
                }
            )

    return card, issues


def _derive_missing_fields(card: dict[str, Any]) -> None:
    if "finished_epi" not in card and "grey_epi" in card:
        card["finished_epi"] = card["grey_epi"]
    if "finished_ppi" not in card and "grey_ppi" in card:
        card["finished_ppi"] = card["grey_ppi"]
    if "fabric_category" not in card and isinstance(card.get("gsm"), (int, float)):
        gsm = float(card["gsm"])
        if gsm < 130:
            card["fabric_category"] = "Light Wt"
        elif gsm < 220:
            card["fabric_category"] = "Top Wt"
        elif gsm < 300:
            card["fabric_category"] = "Mid Wt"
        elif gsm < 450:
            card["fabric_category"] = "Bottom Wt"
        else:
            card["fabric_category"] = "Heavy Wt"
    if "card_ref" not in card:
        card["card_ref"] = "UNNAMED-CARD"


def composition_total(composition: str | None) -> float | None:
    if not composition:
        return None
    values = [float(num) for num in re.findall(r"(\d+(?:\.\d+)?)\s*%", composition)]
    return sum(values) if values else None
