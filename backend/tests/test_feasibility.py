from pathlib import Path

from services.feasibility import check_fabric


PROJECT_DIR = Path(__file__).resolve().parents[2]
SAMPLE = PROJECT_DIR / "data" / "samples" / "sample_cloth_card.txt"


def test_sample_card_runs_22_rules_without_errors():
    result = check_fabric(SAMPLE.read_text(encoding="utf-8"), source_filename=SAMPLE.name)

    assert result["report"]["rules_run"] == 22
    assert result["report"]["gate"] in {"PASS", "WARNING"}
    assert result["report"]["errors"] == []
    assert result["card"]["card_ref"] == "DEMO-FF-001"


def test_bad_composition_blocks_gate():
    text = SAMPLE.read_text(encoding="utf-8").replace("Composition: 100% Cotton", "Composition: 70% Cotton 20% Viscose")
    result = check_fabric(text)

    assert result["report"]["gate"] == "ERROR"
    assert any(issue["code"] == "COMPOSITION_TOTAL_INVALID" for issue in result["report"]["errors"])
