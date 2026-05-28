import { FileUp, Play, RotateCcw } from "lucide-react";

export default function FabricCheck({
  sampleText,
  text,
  setText,
  file,
  setFile,
  busy,
  onRun,
  onLoadSample,
}) {
  function handleFileUpload(event) {
    const uploadedFile = event.target.files?.[0] || null;
    setFile(uploadedFile);
    if (uploadedFile) {
      uploadedFile.text().then((contents) => setText(contents)).catch(() => setText(""));
    }
  }

  return (
    <div className="two-column">
      <section className="panel panel-large">
        <div className="panel-title">
          <h2>Fabric Check</h2>
          <span>{file?.name || "Text input"}</span>
        </div>
        <textarea
          value={text}
          onChange={(event) => {
            setText(event.target.value);
            setFile(null);
          }}
          spellCheck="false"
        />
        <div className="button-row">
          <label className="button button-secondary">
            <FileUp size={16} />
            Upload
            <input
              type="file"
              accept=".txt"
              onChange={handleFileUpload}
            />
          </label>
          <button className="button button-secondary" onClick={onLoadSample} disabled={!sampleText}>
            <RotateCcw size={16} />
            Sample
          </button>
          <button className="button button-primary" onClick={onRun} disabled={busy || (!text.trim() && !file)}>
            <Play size={16} />
            {busy ? "Running" : "Run Check"}
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="panel-title">
          <h2>Parsed Targets</h2>
          <span>Demo</span>
        </div>
        <div className="field-grid">
          <span>GSM</span>
          <strong>GSM / theoretical GSM match</strong>
          <span>Structure</span>
          <strong>Ends, repeat, harness, weave</strong>
          <span>Loom</span>
          <strong>Reed, beam, airjet thresholds</strong>
          <span>Labels</span>
          <strong>K-code article and sticker fields</strong>
        </div>
      </section>
    </div>
  );
}
