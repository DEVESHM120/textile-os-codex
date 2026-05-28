import {
  BadgeCheck,
  CheckCircle2,
  ClipboardCheck,
  Download,
  FileSpreadsheet,
  FileText,
  MessageSquareText,
  Printer,
  RefreshCcw,
  Send,
  Upload,
} from "lucide-react";
import GateBadge from "../components/GateBadge.jsx";
import MetricCard from "../components/MetricCard.jsx";

const demoRawCard = `Card Ref: DEMO-FF-001
Customer: Hackathon Brand
Buyer: Demo Buyer
Fabric Category: Mid Wt Shirting
Construction: 40 Ne cotton warp x 40 Ne cotton weft, 120 x 72 plain weave
Composition: 100% Cotton
Weave: Plain
Loom Type: Airjet
GSM: 212
Theoretical GSM: 205
Finished Width Inches: 58
Reed Count: 72
K1: HMM15W
K2: W11001
K3: C66001
K4: HH01
K5: CT-DA`;

const demoIssues = [
  {
    severity: "WARNING",
    code: "GSM_VARIANCE",
    field: "GSM",
    message: "Printed GSM and theoretical GSM differ by 3.4%.",
    action: "FTC should review tolerance before sampling approval.",
  },
  {
    severity: "WARNING",
    code: "REED_CONFIRMATION",
    field: "Reed Count",
    message: "Reed is available, but loom plan should confirm reed space.",
    action: "Check reed inventory and width compatibility.",
  },
  {
    severity: "INFO",
    code: "LABEL_READY",
    field: "K-code",
    message: "K1-K5 values are sufficient for sticker generation.",
    action: "Proceed to Sticker Agent after approval.",
  },
];

const queueRows = [
  { id: "DEMO-FF-001", designer: "Ananya", status: "ready", gate: "WARNING", age: "18 min", notes: "Awaiting FTC send" },
  { id: "OX-REV-044", designer: "Raghav", status: "needs_revision", gate: "ERROR", age: "1 hr", notes: "Drawing repeat mismatch" },
  { id: "LIN-APP-218", designer: "Meera", status: "approved", gate: "PASS", age: "Today", notes: "Certificate issued" },
];

const stickerPreviewRows = [
  {
    Article: "HMM15W/W11001/C66001/HH01/CT-DA",
    Content: "100% Cotton",
    "Finish GSM": "212",
    Finish: "Cotton Touch + Dobby Approved",
  },
  {
    Article: "A120E413/W22001/C75002/HH03",
    Content: "55% Cotton 45% Viscose",
    "Finish GSM": "186",
    Finish: "Peach Soft",
  },
  {
    Article: "LIN240/W21006/C71004/HH01/WR",
    Content: "70% Linen 30% Cotton",
    "Finish GSM": "165",
    Finish: "Water Repellent",
  },
];

export function DesignerDeskPreview({ workflow, onOpenLiveCheck }) {
  const report = workflow?.feasibility_report || { gate: "WARNING", errors: [], warnings: demoIssues };
  const rawText = workflow?.fabric?.raw_text || demoRawCard;
  const title = workflow?.title || "DEMO-FF-001";

  return (
    <div className="ui-preview-stack">
      <PreviewHero
        eyebrow="Designer Desk"
        title="Submission queue and cloth-card check"
        actionLabel="Open Live Checker"
        onAction={onOpenLiveCheck}
      />

      <div className="metrics-row">
        <MetricCard label="Ready" value="4" tone="success" />
        <MetricCard label="Needs Revision" value="2" tone="warn" />
        <MetricCard label="FTC Submitted" value="6" />
        <MetricCard label="Approved Today" value="3" tone="success" />
      </div>

      <div className="desk-layout">
        <section className="panel queue-panel">
          <div className="panel-title">
            <h2>Designer Submissions</h2>
            <span>Repo parity preview</span>
          </div>
          <div className="queue-list">
            {queueRows.map((row) => (
              <button className="queue-row" type="button" key={row.id}>
                <div>
                  <strong>{row.id}</strong>
                  <span>{row.designer} / {row.notes}</span>
                </div>
                <StatusBadge status={row.status} />
                <GateBadge gate={row.gate} />
              </button>
            ))}
          </div>
        </section>

        <section className="panel upload-preview-panel">
          <div className="panel-title">
            <h2>New Cloth Card</h2>
            <span>.txt upload</span>
          </div>
          <div className="drop-input preview-drop">
            <Upload size={22} />
            <span>Upload cloth card</span>
            <small>Runs all 22 rules and stores raw TXT for review.</small>
          </div>
          <div className="button-row">
            <button className="button button-secondary" type="button">
              <RefreshCcw size={16} />
              Recheck
            </button>
            <button className="button button-primary" type="button">
              <Send size={16} />
              Send to FTC
            </button>
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-title">
          <h2>{title}</h2>
          <GateBadge gate={report.gate} />
        </div>
        <div className="raw-review-grid">
          <div>
            <div className="source-meta">
              <span>View</span>
              <strong>Raw TXT</strong>
              <span>File</span>
              <strong>{workflow?.source_filename || "sample_cloth_card.txt"}</strong>
            </div>
            <pre className="preview-raw-card">{rawText}</pre>
          </div>
          <div className="issue-workspace">
            <IssuePreviewList issues={report.errors?.length ? report.errors : demoIssues} />
            <div className="send-ftc-box">
              <h3>Send to FTC</h3>
              <p>Available when deterministic gate has no blocking errors. Designer note travels with the submission.</p>
              <textarea className="mini-textarea" defaultValue="Please review GSM tolerance and reed planning before sample approval." />
              <button className="button button-primary" type="button">
                <Send size={16} />
                Send for review
              </button>
            </div>
          </div>
        </div>
      </section>

      <MessageThread />
    </div>
  );
}

export function FtcInboxPreview({ workflow }) {
  const title = workflow?.title || "DEMO-FF-001";

  return (
    <div className="ui-preview-stack">
      <PreviewHero eyebrow="FTC Inbox" title="Review, feedback, approval, and certificate" />

      <div className="preview-tabs">
        <button className="active" type="button">Pending Review <strong>6</strong></button>
        <button type="button">Approved <strong>12</strong></button>
        <button type="button">All <strong>28</strong></button>
      </div>

      <div className="ftc-layout">
        <section className="panel">
          <div className="panel-title">
            <h2>Inbox</h2>
            <span>Clickable review queue</span>
          </div>
          <div className="queue-list">
            {queueRows.map((row) => (
              <button className={`queue-row ${row.id === "DEMO-FF-001" ? "active" : ""}`} type="button" key={row.id}>
                <div>
                  <strong>{row.id}</strong>
                  <span>{row.designer} submitted / {row.age}</span>
                </div>
                <StatusBadge status={row.status === "ready" ? "submitted" : row.status} />
              </button>
            ))}
          </div>
        </section>

        <section className="panel ftc-review-panel">
          <div className="panel-title">
            <h2>Review: {title}</h2>
            <GateBadge gate="WARNING" />
          </div>
          <div className="approval-strip">
            <span>Designer: Ananya Sharma</span>
            <span>Submitted: 2026-05-28 19:40</span>
            <span>Rules checked: 22</span>
          </div>
          <div className="raw-review-grid">
            <pre className="preview-raw-card">{workflow?.fabric?.raw_text || demoRawCard}</pre>
            <div className="issue-workspace">
              <IssuePreviewList issues={demoIssues.slice(0, 2)} />
              <div className="button-row">
                <button className="button button-secondary" type="button">
                  <MessageSquareText size={16} />
                  Send Feedback
                </button>
                <button className="button button-primary" type="button">
                  <BadgeCheck size={16} />
                  Approve
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section className="panel certificate-preview">
        <div className="panel-title">
          <h2>Certificate Preview</h2>
          <button className="button button-secondary" type="button">
            <Printer size={16} />
            Print Certificate
          </button>
        </div>
        <div className="certificate-sheet">
          <div>
            <p className="eyebrow">FTC Verified</p>
            <h3>Approved Fabric Feasibility Certificate</h3>
            <span>Approval ID: FTC-DEMO-8A42</span>
          </div>
          <div className="certificate-grid">
            <span>Card Ref</span><strong>{title}</strong>
            <span>Construction</span><strong>40 Ne x 40 Ne / 120 x 72 plain</strong>
            <span>Approved By</span><strong>FTC Demo Member</strong>
            <span>Verification</span><strong>/api/approvals/FTC-DEMO-8A42/verify</strong>
          </div>
        </div>
      </section>
    </div>
  );
}

export function StickerAgentPreview({ uiConfig }) {
  const showStats = uiConfig.stickerPreview !== "table";
  const showVisual = uiConfig.stickerPreview === "visual";

  return (
    <div className="ui-preview-stack sticker-preview-surface">
      <PreviewHero eyebrow="Sticker Agent" title="Generate stickers and convert buyer Excel" />

      <div className="preview-tabs">
        <button className="active" type="button">Generate Stickers</button>
        <button type="button">Convert Excel</button>
      </div>

      <div className="sticker-layout">
        <section className="panel">
          <div className="panel-title">
            <h2>Upload Files</h2>
            <span>Original Sticker-Agent flow</span>
          </div>
          <div className="upload-stack">
            <div className="drop-input preview-drop has-file">
              <FileSpreadsheet size={22} />
              <span>Master Data Excel *</span>
              <small>Master-data.xls.xls / 545 rows detected</small>
            </div>
            <div className="drop-input preview-drop">
              <FileText size={22} />
              <span>Sticker Template</span>
              <small>Optional; default template used if blank.</small>
            </div>
          </div>
          <button className="button button-primary wide-action" type="button">
            <ClipboardCheck size={16} />
            Generate Stickers
          </button>
        </section>

        <section className="panel">
          <div className="panel-title">
            <h2>Convert Excel</h2>
            <span>Old Navy to master format</span>
          </div>
          <div className="drop-input preview-drop has-file">
            <FileSpreadsheet size={22} />
            <span>old navy.xlsx</span>
            <small>Sheets detected: on women, on men, woven tops</small>
          </div>
          <label className="field-label-block">
            Sheet
            <select>
              <option>on women</option>
              <option>on men</option>
              <option>woven tops</option>
            </select>
          </label>
          <button className="button button-secondary wide-action" type="button">
            Convert to Master Format
          </button>
        </section>
      </div>

      <section className="panel result-preview-panel">
        <div className="panel-title">
          <h2>Generation Result</h2>
          <a className="button button-primary" href="#download-preview">
            <Download size={16} />
            Download Stickers (.xlsx)
          </a>
        </div>
        {showStats ? (
          <div className="result-stats">
            <MetricCard label="Total Rows" value="545" />
            <MetricCard label="Generated" value="545" tone="success" />
            <MetricCard label="Errors" value="0" tone="danger" />
          </div>
        ) : null}
        <div className="result-preview-grid">
          {showVisual ? (
            <div className="visual-sticker">
              <span>VARDHMAN ARTICLE</span>
              <strong>HMM15W/W11001/C66001/HH01/CT-DA</strong>
              <span>CONTENT</span>
              <strong>100% Cotton</strong>
              <span>FINISH GSM</span>
              <strong>212</strong>
              <CheckCircle2 size={22} />
            </div>
          ) : null}
          <PreviewTable rows={stickerPreviewRows} />
        </div>
      </section>
    </div>
  );
}

function PreviewHero({ eyebrow, title, actionLabel, onAction }) {
  return (
    <section className="command-surface preview-hero">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
      </div>
      {actionLabel ? (
        <button className="button button-secondary" type="button" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </section>
  );
}

function StatusBadge({ status }) {
  return <span className={`status-badge status-${status}`}>{status.replaceAll("_", " ")}</span>;
}

function IssuePreviewList({ issues }) {
  return (
    <div className="issue-preview-grid">
      {issues.map((issue) => (
        <article className={`issue-preview issue-preview-${String(issue.severity || issue.level || "INFO").toLowerCase()}`} key={issue.code}>
          <div>
            <strong>{issue.code}</strong>
            <span>{issue.field || issue.category || "Technical"}</span>
          </div>
          <p>{issue.message}</p>
          <small>{issue.action || issue.details?.action || "Review before approval."}</small>
        </article>
      ))}
    </div>
  );
}

function MessageThread() {
  return (
    <section className="panel">
      <div className="panel-title">
        <h2>Feedback Thread</h2>
        <span>Designer + FTC</span>
      </div>
      <div className="message-thread">
        <div className="message-row">
          <span className="message-avatar avatar-designer">D</span>
          <div>
            <strong>Designer</strong>
            <p>Submitting after recheck. Reed and GSM are ready for FTC review.</p>
          </div>
        </div>
        <div className="message-row">
          <span className="message-avatar avatar-ftc">F</span>
          <div>
            <strong>FTC</strong>
            <p>Please confirm theoretical GSM basis and attach revised construction sheet.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function PreviewTable({ rows }) {
  const columns = Object.keys(rows[0] || {});
  return (
    <div className="preview-table-wrap">
      <table className="preview-table">
        <thead>
          <tr>
            <th>#</th>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.Article}>
              <td>{index + 1}</td>
              {columns.map((column) => (
                <td key={column}>{row[column]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
