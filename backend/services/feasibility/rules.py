from __future__ import annotations

from typing import Any, Callable

from .parser import composition_total


RuleFn = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any] | None]


DEFAULT_CONFIG = {
    "GSM_TOLERANCE_PCT": 8.0,
    "COVER_FACTOR_LIMIT": 32.0,
    "BEAM_CAPACITY_KG": 800.0,
    "AIRJET_INSERTION_LIMIT": 8.0,
    "MAX_ENDS_PER_DENT": 3.0,
    "LOOM_MAX_REPEAT": 64.0,
    "LOOM_HARNESS_LIMIT": 16.0,
    "COMPOSITION_TOLERANCE_PCT": 1.0,
    "WEIGHT_SUM_TOLERANCE_PCT": 0.5,
    "SELVEDGE_MIN_RATIO": 0.005,
    "EPI_TOLERANCE": 2.0,
    "SHRINKAGE_MIN_PCT": 2.0,
    "SHRINKAGE_MAX_PCT": 12.0,
    "FINISHABILITY_THRESHOLD_PCT": 10.0,
    "FAB_CATEGORY_GSM_RANGES": {
        "Light Wt": (80, 130),
        "Top Wt": (130, 220),
        "Mid Wt": (220, 300),
        "Bottom Wt": (300, 450),
        "Heavy Wt": (450, 9999),
    },
    "KNOWN_REEDS": [48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92],
}


def _num(card: dict[str, Any], field: str) -> float | None:
    value = card.get(field)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _issue(
    severity: str,
    code: str,
    category: str,
    message: str,
    **details: Any,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "code": code,
        "category": category,
        "message": message,
        "details": details,
    }


def check_ends_total(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    body = _num(card, "body_ends")
    selvedge = _num(card, "selvedge_ends") or 0
    total = _num(card, "total_ends")
    if body is None or total is None:
        return None
    expected = body + selvedge
    if abs(expected - total) > 2:
        return _issue("ERROR", "ENDS_TOTAL_MISMATCH", "STRUCTURAL", "Total ends do not match body plus selvedge ends.", expected=expected, value=total, field="total_ends", action="Correct total ends or selvedge ends.")
    return None


def check_peg_drawing_harness(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    repeats = _num(card, "peg_plan_repeats")
    shafts = _num(card, "shaft_count")
    if repeats and shafts and repeats > shafts * 2:
        return _issue("WARNING", "PEG_DRAWING_COMPLEXITY", "STRUCTURAL", "Peg plan repeats look high for the shaft count.", value=repeats, expected=f"<= {shafts * 2}", field="peg_plan_repeats", action="Review peg plan against drawing and harness setup.")
    return None


def check_repeat_feasible(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    repeat = _num(card, "ends_per_repeat")
    if repeat and repeat > cfg["LOOM_MAX_REPEAT"]:
        return _issue("ERROR", "REPEAT_EXCEEDS_LOOM", "STRUCTURAL", "Weave repeat exceeds loom repeat capacity.", value=repeat, expected=cfg["LOOM_MAX_REPEAT"], field="ends_per_repeat", action="Reduce repeat size or assign a loom with higher repeat capacity.")
    return None


def check_harness_limit(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    shafts = _num(card, "shaft_count")
    if shafts and shafts > cfg["LOOM_HARNESS_LIMIT"]:
        return _issue("ERROR", "HARNESS_LIMIT_EXCEEDED", "STRUCTURAL", "Shaft count exceeds configured loom harness limit.", value=shafts, expected=cfg["LOOM_HARNESS_LIMIT"], field="shaft_count", action="Change loom assignment or simplify weave.")
    return None


def check_weave_number(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    if not card.get("weave_number"):
        return _issue("WARNING", "WEAVE_NUMBER_MISSING", "STRUCTURAL", "Weave number is missing.", field="weave_number", action="Add weave number before technical approval.")
    return None


def check_oxford_even_pattern(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    weave = str(card.get("weave", "")).lower()
    repeat = _num(card, "ends_per_repeat")
    if "oxford" in weave and repeat and repeat % 2 != 0:
        return _issue("ERROR", "OXFORD_REPEAT_NOT_EVEN", "STRUCTURAL", "Oxford weave requires an even repeat pattern.", value=repeat, field="ends_per_repeat", action="Use an even repeat for Oxford construction.")
    return None


def check_weave_repeat_boundary(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    total = _num(card, "total_ends")
    repeat = _num(card, "ends_per_repeat")
    if total and repeat and total % repeat != 0:
        return _issue("INFO", "REPEAT_BOUNDARY_OFFSET", "STRUCTURAL", "Total ends do not land exactly on the weave repeat boundary.", value=total, expected=f"multiple of {repeat}", field="total_ends", action="Review repeat boundary at fabric width.")
    return None


def check_pattern_balance(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    body = _num(card, "body_ends")
    repeat = _num(card, "ends_per_repeat")
    if body and repeat and body % repeat not in (0, repeat / 2):
        return _issue("INFO", "PATTERN_BALANCE_REVIEW", "STRUCTURAL", "Body ends may create an unbalanced terminal repeat.", value=body, expected=f"balanced against repeat {repeat}", field="body_ends", action="Review final repeat balance with design team.")
    return None


def check_selvedge_ratio(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    total = _num(card, "total_ends")
    selvedge = _num(card, "selvedge_ends")
    if total and selvedge and selvedge / total > 0.05:
        return _issue("WARNING", "SELVEDGE_RATIO_HIGH", "STRUCTURAL", "Selvedge ends are high compared with total ends.", value=round(selvedge / total * 100, 2), expected="<= 5%", field="selvedge_ends", action="Confirm selvedge plan is intentional.")
    return None


def check_theoretical_gsm(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    printed = _num(card, "gsm")
    theoretical = _num(card, "theoretical_gsm")
    if printed is None:
        return None
    if theoretical is None:
        return None
    delta = abs(printed - theoretical) / max(printed, 1) * 100
    if delta > cfg["GSM_TOLERANCE_PCT"]:
        return _issue("ERROR", "GSM_TOLERANCE_FAIL", "WEIGHT", "Printed GSM and theoretical GSM are outside tolerance.", value=printed, expected=round(theoretical, 2), tolerance_pct=cfg["GSM_TOLERANCE_PCT"], field="gsm", action="Recheck construction, yarn count, crimp, and printed GSM.")
    return None


def check_cover_factor(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    epi = _num(card, "grey_epi")
    ppi = _num(card, "grey_ppi")
    warp = _num(card, "warp_count_ne")
    weft = _num(card, "weft_count_ne")
    if not all([epi, ppi, warp, weft]):
        return None
    cover = (epi / (warp ** 0.5)) + (ppi / (weft ** 0.5))
    if cover > cfg["COVER_FACTOR_LIMIT"]:
        return _issue("WARNING", "COVER_FACTOR_HIGH", "WEIGHT", "Cover factor is above the configured practical limit.", value=round(cover, 2), expected=cfg["COVER_FACTOR_LIMIT"], field="construction", action="Review density and loom feasibility.")
    return None


def check_fabric_category_gsm(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    category = str(card.get("fabric_category", "")).strip()
    gsm = _num(card, "gsm")
    if not category or gsm is None:
        return None
    ranges = cfg["FAB_CATEGORY_GSM_RANGES"]
    matched_category = next((name for name in ranges if name.lower() in category.lower()), None)
    if matched_category:
        low, high = ranges[matched_category]
        if not low <= gsm <= high:
            return _issue("WARNING", "CATEGORY_GSM_MISMATCH", "WEIGHT", "GSM does not match the stated fabric category.", value=gsm, expected=f"{low}-{high}", field="fabric_category", action="Confirm category or update GSM.")
    return None


def check_reed_available(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    reed = _num(card, "reed_count")
    if reed is None:
        return _issue("WARNING", "REED_MISSING", "LOOM", "Reed count is missing.", field="reed_count", action="Add reed count for loom planning.")
    if int(round(reed)) not in cfg["KNOWN_REEDS"]:
        return _issue("WARNING", "REED_NOT_IN_DEMO_INVENTORY", "LOOM", "Reed is not present in demo inventory.", value=reed, expected=cfg["KNOWN_REEDS"], field="reed_count", action="Check mill reed inventory before sampling.")
    return None


def check_reed_load(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    epi = _num(card, "grey_epi")
    reed = _num(card, "reed_count")
    if not epi or not reed:
        return None
    ends_per_dent = epi / reed
    if ends_per_dent > cfg["MAX_ENDS_PER_DENT"]:
        return _issue("ERROR", "REED_LOAD_HIGH", "LOOM", "Ends per dent exceeds safe reed loading.", value=round(ends_per_dent, 2), expected=cfg["MAX_ENDS_PER_DENT"], field="reed_count", action="Select a finer reed or reduce EPI.")
    return None


def check_beam_capacity(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    beam = _num(card, "warp_beam_weight_kg")
    if beam and beam > cfg["BEAM_CAPACITY_KG"]:
        return _issue("ERROR", "BEAM_CAPACITY_EXCEEDED", "LOOM", "Warp beam weight exceeds beam capacity.", value=beam, expected=cfg["BEAM_CAPACITY_KG"], field="warp_beam_weight_kg", action="Reduce beam length or split lot.")
    return None


def check_weft_insertion_feasibility(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    pick_rate = _num(card, "pick_rate_meters_per_min")
    loom = str(card.get("loom_type", "")).lower()
    if "air" in loom and pick_rate and pick_rate > cfg["AIRJET_INSERTION_LIMIT"]:
        return _issue("WARNING", "AIRJET_PICK_RATE_HIGH", "LOOM", "Airjet insertion speed is high for demo threshold.", value=pick_rate, expected=cfg["AIRJET_INSERTION_LIMIT"], field="pick_rate_meters_per_min", action="Confirm machine speed setting before sample run.")
    return None


def check_composition_total(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    total = composition_total(card.get("composition"))
    if total is None:
        return _issue("WARNING", "COMPOSITION_UNPARSED", "YARN", "Composition percentages could not be parsed.", field="composition", action="Use percentage format such as 55% Cotton 45% Viscose.")
    if abs(total - 100) > cfg["COMPOSITION_TOLERANCE_PCT"]:
        return _issue("ERROR", "COMPOSITION_TOTAL_INVALID", "YARN", "Composition percentages do not total 100%.", value=total, expected=100, field="composition", action="Correct fiber composition percentages.")
    return None


def check_count_match(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    warp = _num(card, "warp_count_ne")
    weft = _num(card, "weft_count_ne")
    construction = str(card.get("construction", ""))
    if not construction:
        return None
    if warp and str(int(warp)) not in construction:
        return _issue("WARNING", "WARP_COUNT_NOT_IN_CONSTRUCTION", "YARN", "Warp count is not visible in construction text.", value=warp, field="construction", action="Check yarn count entry against construction string.")
    if weft and str(int(weft)) not in construction:
        return _issue("WARNING", "WEFT_COUNT_NOT_IN_CONSTRUCTION", "YARN", "Weft count is not visible in construction text.", value=weft, field="construction", action="Check yarn count entry against construction string.")
    return None


def check_yarn_weight_sum(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    warp_pct = _num(card, "warp_weight_percent")
    weft_pct = _num(card, "weft_weight_percent")
    if warp_pct is None or weft_pct is None:
        return None
    total = warp_pct + weft_pct
    if abs(total - 100) > cfg["WEIGHT_SUM_TOLERANCE_PCT"]:
        return _issue("ERROR", "YARN_WEIGHT_SUM_INVALID", "YARN", "Warp and weft weight distribution does not total 100%.", value=total, expected=100, field="warp_weight_percent", action="Correct warp/weft weight split.")
    return None


def check_ends_distribution(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    total = _num(card, "total_ends")
    selvedge = _num(card, "selvedge_ends")
    if total and selvedge is not None and selvedge / total < cfg["SELVEDGE_MIN_RATIO"]:
        return _issue("WARNING", "SELVEDGE_RATIO_LOW", "YARN", "Selvedge ends are low compared with total ends.", value=round(selvedge / total * 100, 2), expected=f">= {cfg['SELVEDGE_MIN_RATIO'] * 100:.2f}%", field="selvedge_ends", action="Confirm selvedge construction and drawing plan.")
    return None


def check_width_epi_consistency(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    total = _num(card, "total_ends")
    width = _num(card, "grey_width_inches") or _num(card, "reed_space_inches")
    epi = _num(card, "grey_epi")
    if not all([total, width, epi]):
        return None
    calculated = total / width
    if abs(calculated - epi) > cfg["EPI_TOLERANCE"]:
        return _issue("WARNING", "WIDTH_EPI_INCONSISTENT", "SHRINKAGE_WIDTH", "Width and total ends imply a different EPI.", value=round(calculated, 2), expected=epi, field="grey_epi", action="Review reed space, total ends, and EPI.")
    return None


def check_shrinkage_gry_fin(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    grey = _num(card, "grey_width_inches")
    finished = _num(card, "finished_width_inches")
    if not grey or not finished:
        return None
    shrinkage = (grey - finished) / grey * 100
    if shrinkage < cfg["SHRINKAGE_MIN_PCT"] or shrinkage > cfg["SHRINKAGE_MAX_PCT"]:
        return _issue("WARNING", "WIDTH_SHRINKAGE_OUT_OF_RANGE", "SHRINKAGE_WIDTH", "Grey to finished width shrinkage is outside expected range.", value=round(shrinkage, 2), expected=f"{cfg['SHRINKAGE_MIN_PCT']}-{cfg['SHRINKAGE_MAX_PCT']}%", field="finished_width_inches", action="Review finishing route and width target.")
    return None


def check_shrinkage_finishability(card: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any] | None:
    grey_epi = _num(card, "grey_epi")
    finished_epi = _num(card, "finished_epi")
    if not grey_epi or not finished_epi:
        return None
    finishability = abs(finished_epi - grey_epi) / grey_epi * 100
    if finishability > cfg["FINISHABILITY_THRESHOLD_PCT"]:
        return _issue("ERROR", "FINISHABILITY_THRESHOLD_EXCEEDED", "SHRINKAGE_WIDTH", "Finished EPI change exceeds finishability threshold.", value=round(finishability, 2), expected=f"<= {cfg['FINISHABILITY_THRESHOLD_PCT']}%", field="finished_epi", action="Review finishing target before sampling.")
    return None


ALL_RULES: list[RuleFn] = [
    check_ends_total,
    check_peg_drawing_harness,
    check_repeat_feasible,
    check_harness_limit,
    check_weave_number,
    check_oxford_even_pattern,
    check_weave_repeat_boundary,
    check_pattern_balance,
    check_theoretical_gsm,
    check_cover_factor,
    check_fabric_category_gsm,
    check_reed_available,
    check_reed_load,
    check_beam_capacity,
    check_weft_insertion_feasibility,
    check_composition_total,
    check_count_match,
    check_yarn_weight_sum,
    check_ends_distribution,
    check_width_epi_consistency,
    check_shrinkage_gry_fin,
    check_shrinkage_finishability,
]
