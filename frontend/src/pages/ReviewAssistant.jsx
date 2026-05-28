import { useEffect, useState } from "react";
import { FileText, Table2, WandSparkles } from "lucide-react";
import GateBadge from "../components/GateBadge.jsx";
import IssueList from "../components/IssueList.jsx";

export default function ReviewAssistant({ workflow, aiSummary, busy, onGenerateAi }) {
  const [sourceView, setSourceView] = useState("raw");
  const report = workflow?.feasibility_report || {};
  const parsed = workflow?.fabric?.parsed || {};
  const rawText = workflow?.fabric?.raw_text || "";
  const sourceFilename = workflow?.source_filename || parsed.source_filename || "manual-entry.txt";

  useEffect(() => {
    setSourceView("raw");
  }, [workflow?.id]);

  return (
    <div className="view-grid">
      <section className="command-surface">
        <div>
          <p className="eyebrow">Feasibility result</p>
          <h1>{workflow?.title || "No workflow selected"}</h1>
        </div>
        <GateBadge gate={report.gate} />
      </section>

      <div className="review-layout">
        <section className="panel panel-large">
          <div className="panel-title">
            <h2>Raw Uploaded TXT</h2>
            <div className="segmented">
              <button className={sourceView === "raw" ? "active" : ""} onClick={() => setSourceView("raw")}>
                <FileText size={15} />
                Raw
              </button>
              <button className={sourceView === "parsed" ? "active" : ""} onClick={() => setSourceView("parsed")}>
                <Table2 size={15} />
                Parsed
              </button>
            </div>
          </div>
          <div className="source-meta">
            <span>File</span>
            <strong>{sourceFilename}</strong>
            <span>View</span>
            <strong>{sourceView === "raw" ? "Raw TXT" : "Parsed Fields"}</strong>
          </div>
          {sourceView === "raw" ? (
            <pre className="raw-card-pre">{rawText || "No raw card text available."}</pre>
          ) : (
            <div className="parsed-table">
              {Object.entries(parsed).map(([key, value]) => (
                <div className="parsed-row" key={key}>
                  <span>{key.replaceAll("_", " ")}</span>
                  <strong>{String(value ?? "")}</strong>
                </div>
              ))}
            </div>
          )}
        </section>

        <div className="issue-stack">
          <IssueList title="Errors" issues={report.errors || []} emptyText="No blocking issues." />
          <IssueList title="Warnings" issues={report.warnings || []} emptyText="No warnings." />
        </div>
      </div>

      <section className="panel">
        <div className="panel-title">
          <h2>AI Assistant</h2>
          <button className="button button-primary" onClick={onGenerateAi} disabled={!workflow || busy}>
            <WandSparkles size={16} />
            {busy ? "Drafting" : "Generate"}
          </button>
        </div>
        {aiSummary ? (
          <div className="assistant-output">
            <p>{aiSummary.risk_summary}</p>
            <div className="field-grid">
              <span>Missing</span>
              <strong>{aiSummary.missing_fields?.join(", ") || "None"}</strong>
              <span>Label Copy</span>
              <strong>{aiSummary.label_copy}</strong>
              <span>Technical Sheet</span>
              <strong>{aiSummary.technical_sheet_text}</strong>
              <span>Source</span>
              <strong>{aiSummary.source}</strong>
            </div>
            <div className="chips">
              {(aiSummary.correction_suggestions || []).map((item, index) => (
                <span key={`${item}-${index}`}>{item}</span>
              ))}
            </div>
          </div>
        ) : (
          <p className="muted">Generate a structured communication draft for the current fabric record.</p>
        )}
      </section>
    </div>
  );
}
