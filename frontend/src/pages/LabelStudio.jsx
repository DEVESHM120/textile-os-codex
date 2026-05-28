import { useEffect, useState } from "react";
import {
  artifactDownloadUrl,
  fetchStickerTemplates,
  uploadStickerTemplate,
  deleteStickerTemplate,
  generateBulkStickersWithTemplate,
  convertBuyerFile,
} from "../api/client.js";

export default function LabelStudio({
  bulkArtifact,
  convertArtifact,
  bulkBusy,
  convertBusy,
  onGenerateBulkStickers,
  onConvertExcel,
}) {
  const [tab, setTab] = useState("generate");

  return (
    <div className="sticker-agent-page">
      <div className="agent-tabs">
        <button
          className={`agent-tab ${tab === "generate" ? "active" : ""}`}
          onClick={() => setTab("generate")}
        >
          ⚡ Generate Stickers
        </button>
        <button
          className={`agent-tab ${tab === "convert" ? "active" : ""}`}
          onClick={() => setTab("convert")}
        >
          🔄 Convert Excel
        </button>
      </div>

      {tab === "generate" && (
        <GenerateTab
          bulkArtifact={bulkArtifact}
          bulkBusy={bulkBusy}
          onGenerateBulkStickers={onGenerateBulkStickers}
        />
      )}

      {tab === "convert" && (
        <ConvertTab
          convertArtifact={convertArtifact}
          convertBusy={convertBusy}
          onConvertExcel={onConvertExcel}
        />
      )}
    </div>
  );
}

/* ─── Generate Tab ─────────────────────────────────────────────────────────── */

function GenerateTab({ bulkArtifact, bulkBusy, onGenerateBulkStickers }) {
  const [templates, setTemplates]     = useState([]);
  const [selectedId, setSelectedId]   = useState(null);
  const [previewTpl, setPreviewTpl]   = useState(null);
  const [showAdd, setShowAdd]         = useState(false);
  const [masterFile, setMasterFile]   = useState(null);
  const [generateError, setGenerateError] = useState("");
  const [templatesError, setTemplatesError] = useState("");

  useEffect(() => { loadTemplates(); }, []);

  async function loadTemplates() {
    setTemplatesError("");
    try {
      const data = await fetchStickerTemplates();
      setTemplates(data);
      // Auto-select the default (is_default=1)
      const def = data.find(t => t.is_default) || data[0];
      if (def) { setSelectedId(def.id); setPreviewTpl(def); }
    } catch (e) {
      setTemplatesError(e.message);
    }
  }

  function selectTemplate(tpl) {
    setSelectedId(tpl.id);
    setPreviewTpl(tpl);
    setShowAdd(false);
  }

  async function handleDelete(e, tplId) {
    e.stopPropagation();
    if (!confirm("Delete this template?")) return;
    try {
      await deleteStickerTemplate(tplId);
      await loadTemplates();
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleGenerate() {
    if (!masterFile) return;
    setGenerateError("");
    try {
      await onGenerateBulkStickers({ masterFile, templateId: selectedId });
    } catch (e) {
      setGenerateError(e.message);
    }
  }

  return (
    <div className="agent-body">

      {/* ── Template chooser ── */}
      <section className="panel agent-card">
        <div className="agent-section-header">
          <h3>Choose Template</h3>
          <button
            className="btn-add-template"
            onClick={() => setShowAdd(s => !s)}
            title="Upload a new template"
          >
            {showAdd ? "✕ Cancel" : "+ Add Template"}
          </button>
        </div>

        {templatesError && <p className="agent-error">{templatesError}</p>}

        <div className="template-grid">
          {templates.map(tpl => (
            <button
              key={tpl.id}
              className={`template-card ${selectedId === tpl.id ? "selected" : ""}`}
              onClick={() => selectTemplate(tpl)}
            >
              <div className="template-card-header">
                <span className="template-name">{tpl.name}</span>
                {tpl.is_default ? (
                  <span className="template-badge">Default</span>
                ) : (
                  <button
                    className="template-delete"
                    onClick={(e) => handleDelete(e, tpl.id)}
                    title="Delete template"
                  >✕</button>
                )}
              </div>
              <p className="template-desc">{tpl.description || "Custom template"}</p>
              <div className="template-fields-mini">
                {(tpl.field_mapping || []).slice(0, 4).map((f, i) => (
                  <span key={i} className="field-chip">{f.label}</span>
                ))}
                {tpl.field_mapping?.length > 4 && (
                  <span className="field-chip field-chip-more">+{tpl.field_mapping.length - 4}</span>
                )}
              </div>
            </button>
          ))}
        </div>

        {showAdd && (
          <AddTemplateForm
            onAdded={async (newTpl) => {
              setShowAdd(false);
              await loadTemplates();
              setSelectedId(newTpl.id);
              setPreviewTpl(newTpl);
            }}
          />
        )}
      </section>

      {/* ── Template preview ── */}
      {previewTpl && (
        <section className="panel agent-card">
          <div className="agent-section-header">
            <h3>Template Preview — {previewTpl.name}</h3>
          </div>
          <TemplatePreview template={previewTpl} />
        </section>
      )}

      {/* ── Upload master + generate ── */}
      <section className="panel agent-card">
        <div className="agent-section-header">
          <h3>Upload Master Data & Generate</h3>
        </div>

        <FileDrop
          label="Master Data Excel"
          hint=".xls / .xlsx — one fabric or roll per row"
          file={masterFile}
          accept=".xls,.xlsx"
          required
          onChange={setMasterFile}
        />

        {generateError && <p className="agent-error">{generateError}</p>}

        <button
          className="button button-primary agent-action-btn"
          onClick={handleGenerate}
          disabled={!masterFile || !selectedId || bulkBusy}
        >
          {bulkBusy ? "Generating…" : "⚡ Generate Stickers"}
        </button>
      </section>

      {/* ── Result ── */}
      {bulkArtifact && (
        <section className="panel agent-card">
          <div className="agent-section-header">
            <h3>Result</h3>
            <span className="muted-text">{bulkArtifact.filename}</span>
          </div>
          <div className="stats-row">
            <StatBadge label="Total Rows"  value={bulkArtifact.rows    ?? "—"} color="blue"  />
            <StatBadge label="Generated"   value={bulkArtifact.success ?? "—"} color="green" />
            <StatBadge
              label="Errors"
              value={Math.max(0, (bulkArtifact.rows ?? 0) - (bulkArtifact.success ?? 0))}
              color="red"
            />
          </div>
          <a
            className="button button-primary agent-download-btn"
            href={artifactDownloadUrl(bulkArtifact.download_url)}
            download
          >
            ⬇ Download Stickers (.xlsx)
          </a>
          {bulkArtifact.preview?.length > 0 && (
            <div className="agent-preview">
              <h4 className="agent-preview-heading">Preview (first 10 rows)</h4>
              <div className="preview-table-wrap">
                <table className="preview-table">
                  <thead>
                    <tr>{Object.keys(bulkArtifact.preview[0]).map(k => <th key={k}>{k}</th>)}</tr>
                  </thead>
                  <tbody>
                    {bulkArtifact.preview.slice(0, 10).map((row, i) => (
                      <tr key={i}>
                        {Object.values(row).map((v, j) => <td key={j}>{v ?? ""}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

/* ─── Template Preview Card ─────────────────────────────────────────────────── */

function TemplatePreview({ template }) {
  const fields = template.field_mapping || [];
  const FIELD_COLORS = {
    VARDHMAN_ARTICLE: "#1f6f78",
    Content:          "#315b4f",
    Construction:     "#4a7c6a",
    Width:            "#5a8a7a",
    "Finish GSM":     "#6a9a8a",
    DYEING_METHOD:    "#7aaa9a",
    FINISH_FULL:      "#8abaa8",
    COUNTRY:          "#9acab8",
  };

  return (
    <div className="template-preview-wrap">
      {/* Left: sticker visual mockup */}
      <div className="sticker-mockup">
        <div className="sticker-mockup-header">
          <span className="sticker-mockup-logo">🏷 Fabric Sticker</span>
        </div>
        <div className="sticker-mockup-body">
          {fields.map((f, i) => (
            <div key={i} className="sticker-mockup-row">
              <span
                className="sticker-mockup-label"
                style={{ borderLeftColor: FIELD_COLORS[f.field] || "#aaa" }}
              >
                {f.label}
              </span>
              <span className="sticker-mockup-value">—</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right: field mapping table */}
      <div className="template-field-table">
        <table className="preview-table">
          <thead>
            <tr>
              <th>Label in Template</th>
              <th>Maps to Field</th>
              <th>Cell</th>
            </tr>
          </thead>
          <tbody>
            {fields.map((f, i) => (
              <tr key={i}>
                <td><strong>{f.label}</strong></td>
                <td><code>{f.field}</code></td>
                <td className="cell-addr">{f.value_cell || f.label_cell || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ─── Add Template Form ─────────────────────────────────────────────────────── */

function AddTemplateForm({ onAdded }) {
  const [name, setName]       = useState("");
  const [desc, setDesc]       = useState("");
  const [file, setFile]       = useState(null);
  const [busy, setBusy]       = useState(false);
  const [error, setError]     = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) { setError("Please choose a .xlsx template file."); return; }
    setBusy(true);
    setError("");
    try {
      const result = await uploadStickerTemplate({ file, name: name.trim(), description: desc.trim() });
      onAdded(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="add-template-form" onSubmit={handleSubmit}>
      <h4 className="add-template-title">Add New Template</h4>

      <label className="field-label-block">
        Template Name
        <input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="e.g. Export Label, Inner Tag…"
        />
      </label>

      <label className="field-label-block">
        Description (optional)
        <input
          value={desc}
          onChange={e => setDesc(e.target.value)}
          placeholder="Short description of this template"
        />
      </label>

      <FileDrop
        label="Template File (.xlsx)"
        hint="Upload your Excel template — label cells will be auto-detected"
        file={file}
        accept=".xlsx"
        required
        onChange={setFile}
      />

      {error && <p className="agent-error">{error}</p>}

      <button
        className="button button-primary"
        type="submit"
        disabled={!file || busy}
      >
        {busy ? "Uploading…" : "Upload Template"}
      </button>
    </form>
  );
}

/* ─── Convert Tab ───────────────────────────────────────────────────────────── */

function ConvertTab({ convertArtifact, convertBusy, onConvertExcel }) {
  const [convertFile, setConvertFile] = useState(null);
  const [sheetName, setSheetName]     = useState("");
  const [convertError, setConvertError] = useState("");

  async function handleConvert() {
    setConvertError("");
    try {
      await onConvertExcel({ convertFile, sheetName });
    } catch (e) {
      setConvertError(e.message);
    }
  }

  return (
    <div className="agent-body">
      <section className="panel agent-card">
        <div className="agent-section-header">
          <h3>Convert Unorganized Excel → Master Format</h3>
        </div>
        <p className="muted">
          Upload an Old-Navy style Excel (comma-in-cell format) to convert it into the standard master format.
        </p>

        <FileDrop
          label="Unorganized Excel File"
          hint=".xlsx — comma-in-cell buyer format"
          file={convertFile}
          accept=".xlsx"
          required
          onChange={setConvertFile}
        />

        <label className="field-label-block">
          Sheet name (optional)
          <input
            value={sheetName}
            onChange={e => setSheetName(e.target.value)}
            placeholder="Leave blank for first sheet"
          />
        </label>

        {convertError && <p className="agent-error">{convertError}</p>}

        <button
          className="button button-primary agent-action-btn"
          onClick={handleConvert}
          disabled={!convertFile || convertBusy}
        >
          {convertBusy ? "Converting…" : "🔄 Convert to Master Format"}
        </button>
      </section>

      {convertArtifact && (
        <section className="panel agent-card">
          <div className="agent-section-header">
            <h3>Result</h3>
            <span className="muted-text">{convertArtifact.filename}</span>
          </div>
          <div className="stats-row">
            <StatBadge label="Rows Converted" value={convertArtifact.rows ?? "—"} color="blue" />
          </div>
          <a
            className="button button-primary agent-download-btn"
            href={artifactDownloadUrl(convertArtifact.download_url)}
            download
          >
            ⬇ Download Organized Excel (.xlsx)
          </a>
        </section>
      )}
    </div>
  );
}

/* ─── Shared components ─────────────────────────────────────────────────────── */

function StatBadge({ label, value, color }) {
  return (
    <div className={`stat-badge stat-${color}`}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function FileDrop({ label, hint, file, accept, required = false, onChange }) {
  return (
    <label className={`file-drop-zone ${file ? "has-file" : ""}`}>
      <input
        type="file"
        accept={accept}
        onChange={e => onChange(e.target.files?.[0] || null)}
        style={{ display: "none" }}
      />
      <span className="file-drop-icon">📂</span>
      <div className="file-drop-text">
        <strong>
          {label} {required && <span className="required-star">*</span>}
        </strong>
        <span>{file ? file.name : `Drag & drop or browse — ${hint}`}</span>
      </div>
      {file && (
        <button
          type="button"
          className="file-drop-remove"
          onClick={e => { e.preventDefault(); onChange(null); }}
        >✕</button>
      )}
    </label>
  );
}
