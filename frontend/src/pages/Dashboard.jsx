import { ClipboardCheck, FileSpreadsheet, Gauge, WandSparkles } from "lucide-react";
import GateBadge from "../components/GateBadge.jsx";
import MetricCard from "../components/MetricCard.jsx";

export default function Dashboard({ workflow, recent = [], onSelectView, onOpenWorkflow }) {
  const report = workflow?.feasibility_report;
  const artifacts = workflow?.artifacts || [];
  return (
    <div className="view-grid">
      <section className="command-surface">
        <div>
          <p className="eyebrow">Active workflow</p>
          <h1>{workflow?.title || "No fabric workflow loaded"}</h1>
        </div>
        {report ? <GateBadge gate={report.gate} /> : null}
      </section>

      <div className="metrics-row">
        <MetricCard label="Rules run" value={report?.rules_run ?? 22} />
        <MetricCard label="Errors" value={report?.errors?.length ?? 0} tone="danger" />
        <MetricCard label="Warnings" value={report?.warnings?.length ?? 0} tone="warn" />
        <MetricCard label="Artifacts" value={artifacts.length} tone="success" />
      </div>

      <section className="action-grid">
        <button className="action-tile" onClick={() => onSelectView("fabric")}>
          <ClipboardCheck size={22} />
          <span>Fabric Check</span>
        </button>
        <button className="action-tile" onClick={() => onSelectView("review")} disabled={!workflow}>
          <WandSparkles size={22} />
          <span>AI Review</span>
        </button>
        <button className="action-tile" onClick={() => onSelectView("labels")} disabled={!workflow}>
          <FileSpreadsheet size={22} />
          <span>Label Studio</span>
        </button>
        <button className="action-tile" onClick={() => onSelectView("artifacts")} disabled={!workflow}>
          <Gauge size={22} />
          <span>Artifacts</span>
        </button>
      </section>

      <section className="panel">
        <div className="panel-title">
          <h2>Recent Workflows</h2>
          <span>{recent.length}</span>
        </div>
        <div className="recent-list">
          {recent.length === 0 ? <p className="muted">Run a cloth card to populate this queue.</p> : null}
          {recent.map((item) => (
            <button className="recent-row" key={item.id} onClick={() => onOpenWorkflow(item.id)}>
              <span>{item.title}</span>
              <GateBadge gate={item.gate} />
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
