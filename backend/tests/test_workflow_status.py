import sqlite3

from db.workflow_db import create_submission, init_workflow_tables


def _create_status(tmp_path, report):
    db_path = tmp_path / "workflow.db"
    init_workflow_tables(db_path)
    submission_id = create_submission(
        db_path,
        designer_id=1,
        card_ref="TEST-001",
        card_filename="test.txt",
        card_raw_text="Card Ref: TEST-001",
        card_parsed={"card_ref": "TEST-001"},
        check_result=report,
    )
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT status FROM submissions WHERE id=?", (submission_id,)).fetchone()[0]


def test_only_pass_can_move_to_ready(tmp_path):
    report = {
        "gate": "PASS",
        "warnings": [],
    }

    assert _create_status(tmp_path, report) == "ready"


def test_feasibility_warning_stays_draft_until_corrected(tmp_path):
    report = {
        "gate": "WARNING",
        "warnings": [
            {
                "code": "COVER_FACTOR_HIGH",
                "category": "WEIGHT",
            }
        ],
    }

    assert _create_status(tmp_path, report) == "draft"


def test_data_completeness_warning_stays_draft(tmp_path):
    report = {
        "gate": "WARNING",
        "warnings": [
            {
                "code": "MISSING_REQUIRED_FIELD",
                "category": "DATA_COMPLETENESS",
            }
        ],
    }

    assert _create_status(tmp_path, report) == "draft"
