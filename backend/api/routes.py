from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from db import (
    create_artifact,
    create_workflow,
    get_artifact,
    get_workflow,
    init_db,
    init_workflow_tables,
    list_recent_workflows,
    record_decision_event,
    save_ai_summary,
    init_template_tables,
    seed_default_template,
    list_templates,
    get_template,
    save_template,
    delete_template,
)
from services.ai import build_ai_summary
from services.artifacts import artifact_path, ensure_artifact_dir
from services.feasibility import check_fabric
from services.stickers import (
    convert_buyer_file,
    generate_bulk_stickers,
    generate_stickers,
    inspect_template,
)


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = Path(__file__).resolve().parents[2]
SAMPLE_CARD = PROJECT_DIR / "data" / "samples" / "sample_cloth_card.txt"


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    load_dotenv(PROJECT_DIR / ".env")
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

    runtime_dir = Path(os.getenv("TEXTILE_RUNTIME_DIR", PROJECT_DIR / ".runtime"))
    if not runtime_dir.is_absolute():
        runtime_dir = PROJECT_DIR / runtime_dir
    if test_config:
        runtime_dir = Path(test_config.get("RUNTIME_DIR", runtime_dir))

    app.config["RUNTIME_DIR"]          = runtime_dir
    app.config["DB_PATH"]              = runtime_dir / "textile_workflow.db"
    app.config["MAX_CONTENT_LENGTH"]   = 25 * 1024 * 1024
    app.config["SECRET_KEY"]           = os.getenv("FF_SECRET_KEY", "dev-insecure-key-change-in-prod")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    ensure_artifact_dir(runtime_dir)
    templates_dir = runtime_dir / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    app.config["TEMPLATES_DIR"] = templates_dir
    init_db(app.config["DB_PATH"])
    init_workflow_tables(app.config["DB_PATH"])
    init_template_tables(app.config["DB_PATH"])
    seed_default_template(app.config["DB_PATH"])

    # Auth manager
    from auth import AuthManager
    _auth = AuthManager(db_path=app.config["DB_PATH"])
    _auth.seed_default_users()
    app.config["AUTH_MANAGER"] = _auth

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "service": "textile-workflow-platform"})

    @app.get("/api/samples/cloth-card")
    def sample_cloth_card():
        return jsonify({"filename": SAMPLE_CARD.name, "text": SAMPLE_CARD.read_text(encoding="utf-8")})

    @app.post("/api/fabric/check")
    def api_fabric_check():
        try:
            text, filename = _extract_text_payload()
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        result = check_fabric(text, source_filename=filename)
        return jsonify(result)

    @app.get("/api/workflows")
    def api_list_workflows():
        return jsonify({"workflows": list_recent_workflows(app.config["DB_PATH"])})

    @app.post("/api/workflows")
    def api_create_workflow():
        try:
            text, filename = _extract_text_payload()
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        result = check_fabric(text, source_filename=filename)
        card = result["card"]
        report = result["report"]
        title = card.get("card_ref") or filename or "Fabric workflow"
        workflow_id = create_workflow(
            app.config["DB_PATH"],
            title=str(title),
            source_filename=filename,
            raw_text=text,
            parsed_card=card,
            report=report,
        )
        workflow = get_workflow(app.config["DB_PATH"], workflow_id)
        return jsonify({"workflow": workflow}), 201

    @app.get("/api/workflows/<int:workflow_id>")
    def api_get_workflow(workflow_id: int):
        workflow = get_workflow(app.config["DB_PATH"], workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404
        return jsonify({"workflow": workflow})

    @app.post("/api/workflows/<int:workflow_id>/ai-summary")
    def api_ai_summary(workflow_id: int):
        workflow = get_workflow(app.config["DB_PATH"], workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404
        summary = build_ai_summary(workflow)
        save_ai_summary(app.config["DB_PATH"], workflow_id, summary)
        return jsonify({"summary": summary})

    @app.post("/api/workflows/<int:workflow_id>/generate-labels")
    def api_generate_labels(workflow_id: int):
        workflow = get_workflow(app.config["DB_PATH"], workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404

        summary = workflow.get("ai_summary") or build_ai_summary(workflow)
        if not workflow.get("ai_summary"):
            save_ai_summary(app.config["DB_PATH"], workflow_id, summary)

        output = generate_stickers(
            workflow["fabric"]["parsed"],
            output_dir=ensure_artifact_dir(app.config["RUNTIME_DIR"]),
            workflow_id=workflow_id,
            label_copy=summary,
        )
        artifact_id = create_artifact(
            app.config["DB_PATH"],
            workflow_id=workflow_id,
            artifact_type="label_workbook",
            filename=output["filename"],
            mime_type=output["mime_type"],
            meta={"preview": output["preview"]},
        )
        record_decision_event(
            app.config["DB_PATH"],
            workflow_id,
            "labels_generated",
            {"artifact_id": artifact_id, "filename": output["filename"]},
        )
        return jsonify(
            {
                "artifact": {
                    "id": artifact_id,
                    "filename": output["filename"],
                    "download_url": f"/api/artifacts/{artifact_id}/download",
                    "preview": output["preview"],
                }
            }
        )

    @app.get("/api/sticker-templates")
    def api_list_sticker_templates():
        return jsonify(list_templates(app.config["DB_PATH"]))

    @app.post("/api/sticker-templates")
    def api_upload_sticker_template():
        if "file" not in request.files:
            return jsonify({"error": "Upload a .xlsx template file as field 'file'."}), 400
        upload = request.files["file"]
        if not upload.filename.lower().endswith(".xlsx"):
            return jsonify({"error": "Template must be .xlsx."}), 400
        name = (request.form.get("name") or "").strip() or Path(upload.filename).stem
        description = (request.form.get("description") or "").strip()
        uid = uuid.uuid4().hex[:8]
        filename = f"template_{uid}.xlsx"
        save_path = app.config["TEMPLATES_DIR"] / filename
        upload.save(str(save_path))
        spec = inspect_template(save_path)
        template_id = save_template(
            app.config["DB_PATH"],
            name=name,
            description=description,
            filename=filename,
            field_mapping=spec["mapping"],
        )
        return jsonify(get_template(app.config["DB_PATH"], template_id)), 201

    @app.delete("/api/sticker-templates/<int:template_id>")
    def api_delete_sticker_template(template_id: int):
        if not delete_template(app.config["DB_PATH"], template_id):
            return jsonify({"error": "Template not found or is the built-in default."}), 404
        return jsonify({"ok": True})

    @app.post("/api/stickers/convert")
    def api_convert_sticker_file():
        if "file" not in request.files:
            return jsonify({"error": "Upload a .xlsx buyer file as field 'file'."}), 400
        upload = request.files["file"]
        if not upload.filename.lower().endswith(".xlsx"):
            return jsonify({"error": "MVP converter accepts .xlsx files."}), 400
        sheet_name = request.form.get("sheet_name") or None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            upload.save(tmp.name)
            tmp_path = Path(tmp.name)
        try:
            output = convert_buyer_file(
                tmp_path,
                output_dir=ensure_artifact_dir(app.config["RUNTIME_DIR"]),
                sheet_name=sheet_name,
            )
        finally:
            tmp_path.unlink(missing_ok=True)
        artifact_id = create_artifact(
            app.config["DB_PATH"],
            workflow_id=None,
            artifact_type="converted_master",
            filename=output["filename"],
            mime_type=output["mime_type"],
            meta={"rows": output["rows"], "columns": output["columns"]},
        )
        return jsonify(
            {
                "artifact": {
                    "id": artifact_id,
                    "filename": output["filename"],
                    "rows": output["rows"],
                    "download_url": f"/api/artifacts/{artifact_id}/download",
                }
            }
        )

    @app.post("/api/stickers/generate-bulk")
    def api_generate_bulk_stickers():
        if "master" not in request.files:
            return jsonify({"error": "Upload master Excel as field 'master'."}), 400

        master = request.files["master"]
        if not _is_excel(master.filename):
            return jsonify({"error": "Master file must be .xls or .xlsx."}), 400

        sheet_name = request.form.get("sheet_name") or None
        master_suffix = Path(master.filename).suffix.lower() or ".xlsx"
        template_path = None
        owned_template = False  # whether we created a tmp file we must delete

        with tempfile.NamedTemporaryFile(delete=False, suffix=master_suffix) as master_tmp:
            master.save(master_tmp.name)
            master_path = Path(master_tmp.name)

        try:
            # Priority 1: template_id (stored template)
            template_id_raw = request.form.get("template_id")
            if template_id_raw:
                tmpl = get_template(app.config["DB_PATH"], int(template_id_raw))
                if tmpl and tmpl.get("filename"):
                    candidate = app.config["TEMPLATES_DIR"] / tmpl["filename"]
                    if candidate.exists():
                        template_path = candidate

            # Priority 2: uploaded template file
            if template_path is None:
                uploaded_tpl = request.files.get("template")
                if uploaded_tpl and uploaded_tpl.filename:
                    if not uploaded_tpl.filename.lower().endswith(".xlsx"):
                        return jsonify({"error": "Template file must be .xlsx."}), 400
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tpl_tmp:
                        uploaded_tpl.save(tpl_tmp.name)
                        template_path = Path(tpl_tmp.name)
                        owned_template = True

            output = generate_bulk_stickers(
                master_path,
                output_dir=ensure_artifact_dir(app.config["RUNTIME_DIR"]),
                template_path=template_path,
                sheet_name=sheet_name,
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        finally:
            master_path.unlink(missing_ok=True)
            if owned_template and template_path:
                template_path.unlink(missing_ok=True)

        artifact_id = create_artifact(
            app.config["DB_PATH"],
            workflow_id=None,
            artifact_type="bulk_label_workbook",
            filename=output["filename"],
            mime_type=output["mime_type"],
            meta={
                "total": output["total"],
                "success": output["success"],
                "mapping": output["mapping"],
                "preview": output["preview"],
            },
        )

        return jsonify(
            {
                "artifact": {
                    "id": artifact_id,
                    "filename": output["filename"],
                    "rows": output["total"],
                    "success": output["success"],
                    "mapping": output["mapping"],
                    "preview": output["preview"],
                    "download_url": f"/api/artifacts/{artifact_id}/download",
                }
            }
        )

    @app.get("/api/artifacts/<int:artifact_id>/download")
    def api_download_artifact(artifact_id: int):
        artifact = get_artifact(app.config["DB_PATH"], artifact_id)
        if not artifact:
            return jsonify({"error": "Artifact not found"}), 404
        path = artifact_path(app.config["RUNTIME_DIR"], artifact["filename"])
        if not path.exists():
            return jsonify({"error": "Artifact file is missing"}), 404
        return send_file(
            path,
            as_attachment=True,
            download_name=secure_filename(artifact["filename"]),
            mimetype=artifact["mime_type"],
        )

    # FTC workflow blueprints
    from api.auth_routes import auth_bp
    from api.ftc_routes import designer_bp, ftc_bp, msg_bp, public_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(designer_bp)
    app.register_blueprint(ftc_bp)
    app.register_blueprint(msg_bp)
    app.register_blueprint(public_bp)

    return app


def _extract_text_payload() -> tuple[str, str]:
    if request.files.get("file"):
        upload = request.files["file"]
        filename = secure_filename(upload.filename or "cloth-card.txt")
        text = upload.read().decode("utf-8", errors="replace")
        return text, filename

    data = request.get_json(silent=True) or {}
    text = str(data.get("text") or "")
    filename = secure_filename(str(data.get("filename") or "manual-entry.txt"))
    if not text.strip():
        raise ValueError("No cloth-card text supplied.")
    return text, filename


def _is_excel(filename: str | None) -> bool:
    return bool(filename and filename.lower().endswith((".xls", ".xlsx")))
