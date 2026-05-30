from io import BytesIO
from pathlib import Path

from api.routes import create_app


PROJECT_DIR = Path(__file__).resolve().parents[2]
SAMPLE = PROJECT_DIR / "data" / "samples" / "sample_cloth_card.txt"


def _login_designer(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "designer1", "password": "designer123"},
    )
    assert response.status_code == 200


def _warning_card_text() -> str:
    return SAMPLE.read_text(encoding="utf-8").replace("Fabric Category: Top Wt", "Fabric Category: Mid Wt")


def test_designer_cannot_send_warning_card_to_ftc(tmp_path):
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()
    _login_designer(client)

    submit = client.post(
        "/api/designer/submit",
        json={"filename": "warning-card.txt", "text": _warning_card_text()},
    )
    assert submit.status_code == 201
    submission = submit.get_json()["submission"]
    assert submission["check_result"]["gate"] == "WARNING"
    assert submission["status"] == "draft"

    send = client.post(f"/api/designer/send/{submission['id']}", json={"note": "Please review"})

    assert send.status_code == 400
    assert "pass" in send.get_json()["error"].lower()


def test_designer_can_reupload_corrected_card_on_same_submission(tmp_path):
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()
    _login_designer(client)

    submit = client.post(
        "/api/designer/submit",
        json={"filename": "warning-card.txt", "text": _warning_card_text()},
    )
    assert submit.status_code == 201
    submission = submit.get_json()["submission"]

    corrected = SAMPLE.read_text(encoding="utf-8")
    reupload = client.post(
        f"/api/designer/reupload/{submission['id']}",
        data={"file": (BytesIO(corrected.encode("utf-8")), "corrected-card.txt")},
        content_type="multipart/form-data",
    )

    assert reupload.status_code == 200
    updated = reupload.get_json()["submission"]
    assert updated["card_filename"] == "corrected-card.txt"
    assert updated["card_raw_text"] == corrected
    assert updated["check_result"]["gate"] == "PASS"
    assert updated["status"] == "ready"
