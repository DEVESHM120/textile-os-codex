from pathlib import Path
from io import BytesIO

import openpyxl

from api.routes import create_app


PROJECT_DIR = Path(__file__).resolve().parents[2]
SAMPLE = PROJECT_DIR / "data" / "samples" / "sample_cloth_card.txt"


def test_workflow_ai_and_label_api(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()

    response = client.post(
        "/api/workflows",
        json={"filename": SAMPLE.name, "text": SAMPLE.read_text(encoding="utf-8")},
    )
    assert response.status_code == 201
    workflow = response.get_json()["workflow"]
    assert workflow["feasibility_report"]["rules_run"] == 22

    ai_response = client.post(f"/api/workflows/{workflow['id']}/ai-summary")
    assert ai_response.status_code == 200
    assert ai_response.get_json()["summary"]["source"] == "fallback"

    label_response = client.post(f"/api/workflows/{workflow['id']}/generate-labels")
    assert label_response.status_code == 200
    artifact = label_response.get_json()["artifact"]
    assert artifact["download_url"].endswith("/download")

    download = client.get(artifact["download_url"])
    assert download.status_code == 200
    assert download.data[:2] == b"PK"


def test_sample_card_endpoint(tmp_path):
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()

    response = client.get("/api/samples/cloth-card")
    assert response.status_code == 200
    assert "DEMO-FF-001" in response.get_json()["text"]


def test_workflow_preserves_raw_uploaded_txt(tmp_path):
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()
    raw_card = (
        "RAW CARD FROM DESIGNER TXT\n"
        "Card Ref: RAW-001\n"
        "Composition: 100% Cotton\n"
        "GSM: 180\n"
        "Designer note: keep this exact line visible for review."
    )

    response = client.post(
        "/api/workflows",
        json={"filename": "designer_raw_card.txt", "text": raw_card},
    )

    assert response.status_code == 201
    workflow = response.get_json()["workflow"]
    assert workflow["source_filename"] == "designer_raw_card.txt"
    assert workflow["fabric"]["raw_text"] == raw_card


def test_bulk_sticker_api(tmp_path):
    app = create_app({"RUNTIME_DIR": tmp_path})
    client = app.test_client()

    stream = BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["K1", "K2", "K3", "Content", "Construction", "Weave", "Width", "Finish GSM"])
    ws.append(["A1", "B2", "C66001", "55%CO 45%VI", "40*40-120*72-150-212", "PLAIN", 150, 212])
    wb.save(stream)
    stream.seek(0)

    response = client.post(
        "/api/stickers/generate-bulk",
        data={"master": (stream, "master.xlsx")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    artifact = response.get_json()["artifact"]
    assert artifact["rows"] == 1
    assert artifact["preview"][0]["Article"] == "A1/B2/C66001"
