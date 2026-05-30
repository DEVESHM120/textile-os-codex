from pathlib import Path

from services.feasibility import check_fabric


PROJECT_DIR = Path(__file__).resolve().parents[2]
SAMPLE = PROJECT_DIR / "data" / "samples" / "sample_cloth_card.txt"


MULTI_COLUMN_CARD = """\
Demo/BA/SA/2025/Designer/SA.0226.0024          CLOTH CARD                      DATE : 19/02/2026
==================================================================================================
Customer   : Demo Mill                               Weave      : DOBBY
Season     : Autumn Winter                           Count      : 20COM*10 OE
CustRef    :                                         Gry.EndPik : 64*50 * 65.00"
Pattern    :                                         Fin.EndPik : 67*52 * 62.00"

REED      : 64/1        WARP TAPE : 100         SLVG ENDS : 64          CPDC REF  :
PICKS/IN. : 50          WEFT TAPE : 100         SLVG DNTS : 32          R.SPC(IN) : 65.00
GMS/SQ.MT : 214.006     GMS/LI.MT : 312.540     GMS/SQ.YD : 178.936     FAB COMP  : 100%CO

Type      : YD          Category  : Casual      Market    : US          Colour    : NA
End use   : Menswear                          Fab Category: Top Wt      Weave Type:
Speciality: Normal                          Design Pattern: NA
WEAVE NO  : 64.64.01                             SELF CREATION REF NO.: Demo

PEG-PLAN (P/R = 64)
DRAWING (E/R = 64) (D/R = 32)

WARPING SECTIONS
SELVEDGE        32    x  1      =     32
BODY ENDS       1     x  4096   =   4096
EXTRA ENDS      0     x  1      =      0
SELVEDGE        32    x  1      =     32
TOTAL                           =   4160

LOOM TYPE: Airjet/8C
"""


def _codes(result, bucket):
    return {issue["code"] for issue in result["report"][bucket]}


def test_sample_card_runs_22_rules_without_false_warnings():
    result = check_fabric(SAMPLE.read_text(encoding="utf-8"), source_filename=SAMPLE.name)

    assert result["report"]["rules_run"] == 22
    assert result["report"]["gate"] == "PASS"
    assert result["report"]["errors"] == []
    assert result["report"]["warnings"] == []
    assert result["card"]["card_ref"] == "DEMO-FF-001"


def test_multi_column_cloth_card_parses_vardhman_style_fields_without_false_warnings():
    result = check_fabric(MULTI_COLUMN_CARD, source_filename="SA.0226.0024.txt")
    card = result["card"]

    assert card["card_ref"] == "SA.0226.0024"
    assert card["customer"] == "Demo Mill"
    assert card["weave"] == "DOBBY"
    assert card["composition"] == "100%CO"
    assert card["gsm"] == 214.006
    assert card["grey_epi"] == 64
    assert card["grey_ppi"] == 50
    assert card["grey_width_inches"] == 65
    assert card["finished_epi"] == 67
    assert card["finished_ppi"] == 52
    assert card["finished_width_inches"] == 62
    assert card["reed_count"] == 64
    assert card["reed_space_inches"] == 65
    assert card["body_ends"] == 4096
    assert card["selvedge_ends"] == 64
    assert card["total_ends"] == 4160
    assert card["ends_per_repeat"] == 64
    assert card["loom_type"] == "Airjet/8C"
    assert result["report"]["gate"] == "PASS"
    assert _codes(result, "warnings") == set()


def test_engineered_repeat_layout_does_not_warn_when_totals_are_consistent():
    card_text = (
        MULTI_COLUMN_CARD
        .replace('Gry.EndPik : 64*50 * 65.00"', 'Gry.EndPik : 68*50 * 61.25"')
        .replace('Fin.EndPik : 67*52 * 62.00"', 'Fin.EndPik : 72*50 * 57.91"')
        .replace("SLVG ENDS : 64", "SLVG ENDS : 114")
        .replace("SELVEDGE        32    x  1      =     32", "SELVEDGE        57    x  1      =     57")
        .replace("BODY ENDS       1     x  4096   =   4096", "BODY ENDS       1     x  4084   =   4084")
        .replace("TOTAL                           =   4160", "TOTAL                           =   4198")
    )

    result = check_fabric(card_text, source_filename="SA.0226.0024.txt")

    assert result["card"]["body_ends"] == 4084
    assert result["card"]["selvedge_ends"] == 114
    assert result["card"]["total_ends"] == 4198
    assert result["report"]["gate"] == "PASS"
    assert "REPEAT_BOUNDARY_OFFSET" not in _codes(result, "warnings")
    assert "PATTERN_BALANCE_REVIEW" not in _codes(result, "warnings")


def test_bad_composition_blocks_gate():
    text = SAMPLE.read_text(encoding="utf-8").replace("Composition: 100% Cotton", "Composition: 70% Cotton 20% Viscose")
    result = check_fabric(text)

    assert result["report"]["gate"] == "ERROR"
    assert any(issue["code"] == "COMPOSITION_TOTAL_INVALID" for issue in result["report"]["errors"])
