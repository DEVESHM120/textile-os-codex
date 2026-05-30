from __future__ import annotations

import re
from typing import Any


FIELD_ALIASES = {
    "card_ref": ["card ref", "reference", "ref", "ref no", "reference no"],
    "customer": ["customer", "brand"],
    "buyer": ["buyer"],
    "fabric_category": ["fabric category", "category", "fab category"],
    "construction": ["construction", "fabric construction"],
    "composition": ["composition", "fabric composition", "content", "fab comp", "fabric comp"],
    "weave": ["weave", "weave structure"],
    "weave_number": ["weave number", "weave no"],
    "loom_type": ["loom type", "loom"],
    "gsm": ["gsm", "finish gsm", "finished gsm", "gms sq mt"],
    "theoretical_gsm": ["theoretical gsm", "calc gsm", "calculated gsm"],
    "grey_epi": ["grey epi", "greige epi"],
    "finished_epi": ["finished epi", "fin epi"],
    "grey_ppi": ["grey ppi", "greige ppi"],
    "finished_ppi": ["finished ppi", "fin ppi"],
    "grey_width_inches": ["grey width inches", "grey width", "greige width"],
    "finished_width_inches": ["finished width inches", "finished width", "fin width"],
    "reed_count": ["reed count", "reed"],
    "reed_space_inches": ["reed space inches", "reed space", "r spc in", "r spc", "rspc in", "rspc"],
    "body_ends": ["body ends"],
    "selvedge_ends": ["selvedge ends", "selvage ends", "slvg ends"],
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
    "season": ["season"],
    "cust_ref": ["custref", "cust ref"],
    "pattern": ["pattern"],
    "count_text": ["count"],
    "grey_endpik": ["gry endpik", "grey endpik", "greige endpik"],
    "finished_endpik": ["fin endpik", "finished endpik"],
    "picks_per_inch": ["picks in"],
    "warp_tape_percent": ["warp tape"],
    "weft_tape_percent": ["weft tape"],
    "selvedge_dents": ["slvg dnts", "selvedge dents"],
    "grams_per_linear_meter": ["gms li mt"],
    "grams_per_square_yard": ["gms sq yd"],
    "end_use": ["end use"],
    "weave_type": ["weave type"],
    "self_creation_ref_no": ["self creation ref no"],
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
    "picks_per_inch",
    "warp_tape_percent",
    "weft_tape_percent",
    "selvedge_dents",
    "grams_per_linear_meter",
    "grams_per_square_yard",
}

KEY_VALUE_PATTERN = re.compile(r"(?:^|\s{2,})(?P<key>[A-Za-z][A-Za-z0-9 ./()&-]{0,35}?)\s*:")
CARD_REF_PATTERN = re.compile(r"\b[A-Z]{1,6}\.\d{4}\.\d{4}\b", re.IGNORECASE)


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
        for key, value in _extract_key_values(raw):
            _set_card_field(card, key, value)

    _derive_from_freeform_text(card, text)

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


def _extract_key_values(line: str) -> list[tuple[str, str]]:
    matches = list(KEY_VALUE_PATTERN.finditer(line))
    if not matches:
        if "=" not in line:
            return []
        key, value = line.split("=", 1)
        if re.search(r"\d", key):
            return []
        return [(key.strip(), value.strip())] if key.strip() and value.strip() else []

    pairs: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        value_start = match.end()
        value_end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
        key = match.group("key").strip()
        value = line[value_start:value_end].strip()
        if key and value:
            pairs.append((key, value))
    return pairs


def _set_card_field(card: dict[str, Any], key: str, value: str) -> None:
    canonical = _normalize_key(key)
    value = value.strip()

    if canonical == "grey_endpik":
        _apply_endpik(card, value, prefix="grey")
        return
    if canonical == "finished_endpik":
        _apply_endpik(card, value, prefix="finished")
        return
    if canonical == "count_text":
        card[canonical] = value
        _apply_yarn_counts(card, value)
        return

    if canonical in NUMERIC_FIELDS:
        card[canonical] = _to_number(value)
    else:
        card[canonical] = value


def _apply_endpik(card: dict[str, Any], value: str, *, prefix: str) -> None:
    numbers = [float(num) for num in re.findall(r"\d+(?:\.\d+)?", value.replace(",", ""))]
    if len(numbers) >= 1:
        card[f"{prefix}_epi"] = numbers[0]
    if len(numbers) >= 2:
        card[f"{prefix}_ppi"] = numbers[1]
    if len(numbers) >= 3:
        card[f"{prefix}_width_inches"] = numbers[2]


def _apply_yarn_counts(card: dict[str, Any], value: str) -> None:
    numbers = [float(num) for num in re.findall(r"\d+(?:\.\d+)?", value.replace(",", ""))]
    if len(numbers) >= 1:
        card.setdefault("warp_count_ne", numbers[0])
    if len(numbers) >= 2:
        card.setdefault("weft_count_ne", numbers[1])


def _derive_from_freeform_text(card: dict[str, Any], text: str) -> None:
    if "card_ref" not in card:
        match = CARD_REF_PATTERN.search(text)
        if match:
            card["card_ref"] = match.group(0).upper()

    if "ends_per_repeat" not in card:
        match = re.search(r"DRAWING\s*\([^)]*E/R\s*=\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
        if match:
            card["ends_per_repeat"] = float(match.group(1))

    _derive_warping_section(card, text)


def _derive_warping_section(card: dict[str, Any], text: str) -> None:
    body_match = re.search(
        r"^\s*BODY ENDS\s+\d+\s*x\s*[\d,]+\s*=\s*([\d,]+)",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    if body_match:
        card["body_ends"] = float(body_match.group(1).replace(",", ""))

    selvedge_values = [
        float(match.replace(",", ""))
        for match in re.findall(
            r"^\s*SELVEDGE\s+\d+\s*x\s*[\d,]+\s*=\s*([\d,]+)",
            text,
            re.IGNORECASE | re.MULTILINE,
        )
    ]
    if selvedge_values:
        card["selvedge_ends"] = sum(selvedge_values)

    total_match = re.search(r"^\s*TOTAL\s*=\s*([\d,]+)", text, re.IGNORECASE | re.MULTILINE)
    if total_match:
        card["total_ends"] = float(total_match.group(1).replace(",", ""))


def _derive_missing_fields(card: dict[str, Any]) -> None:
    if "finished_epi" not in card and "grey_epi" in card:
        card["finished_epi"] = card["grey_epi"]
    if "grey_ppi" not in card and "picks_per_inch" in card:
        card["grey_ppi"] = card["picks_per_inch"]
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
        first_line = str(card.get("source_filename") or "").strip()
        file_ref = CARD_REF_PATTERN.search(first_line)
        if file_ref:
            card["card_ref"] = file_ref.group(0).upper()
    if "construction" not in card:
        count = card.get("count_text")
        epi = card.get("grey_epi")
        ppi = card.get("grey_ppi")
        weave = card.get("weave")
        if count and epi and ppi:
            card["construction"] = f"{count}, {epi:g} x {ppi:g}" + (f" {weave}" if weave else "")
    if "card_ref" not in card:
        card["card_ref"] = "UNNAMED-CARD"


def composition_total(composition: str | None) -> float | None:
    if not composition:
        return None
    values = [float(num) for num in re.findall(r"(\d+(?:\.\d+)?)\s*%", composition)]
    return sum(values) if values else None
