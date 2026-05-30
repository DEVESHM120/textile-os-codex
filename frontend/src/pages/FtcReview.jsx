import { useEffect, useState } from "react";
import {
  fetchFtcSubmission,
  fetchMessages,
  postFtcFeedback,
  approveFtcSubmission,
  postMessage,
  attachmentUrl,
} from "../api/client.js";
import GateBadge from "../components/GateBadge.jsx";
import IssueList from "../components/IssueList.jsx";

const STATUS_LABEL = {
  draft:          "Draft",
  ready:          "Ready",
  submitted:      "Pending Review",
  needs_revision: "Needs Revision",
  approved:       "Approved",
};

const FIELD_LABELS = {
  card_ref: "Card Reference", weave: "Weave", count_raw: "Count (Warp×Weft)",
  warp_count: "Warp Count", weft_count: "Weft Count", grey_epi: "Grey EPI",
  fin_epi: "Finished EPI", grey_ppi: "Grey PPI", fin_ppi: "Finished PPI",
  gsm: "GSM", reed: "Reed", reed_count: "Reed Count", grey_width_inches: "Grey Width (in)",
  fin_width_inches: "Finished Width (in)", body_ends: "Body Ends", total_ends: "Total Ends",
  fabric_composition: "Composition", loom_type: "Loom Type", customer: "Customer",
  season: "Season", pattern: "Pattern", shaft_count: "Shaft Count",
  selvedge_ends: "Selvedge Ends", category: "Category", date: "Date",
};

function fieldLabel(key) {
  return FIELD_LABELS[key] || key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

export default function FtcReview({ subId, currentUser, onDone, onViewCert }) {
  const [sub,          setSub]          = useState(null);
  const [messages,     setMessages]     = useState([]);
  const [feedbackBody, setFeedbackBody] = useState("");
  const [approveNotes, setApproveNotes] = useState("");
  const [msgBody,      setMsgBody]      = useState("");
  const [activeField,  setActiveField]  = useState(null);
  const [cardView,     setCardView]     = useState("raw");
  const [busy,         setBusy]         = useState("");
  const [error,        setError]        = useState("");

  useEffect(() => {
    if (subId) loadSub();
  }, [subId]);

  async function loadSub() {
    setBusy("loading");
    setError("");
    try {
      const [data, msgs] = await Promise.all([
        fetchFtcSubmission(subId),
        fetchMessages(subId),
      ]);
      setSub(data);
      setMessages(msgs);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  async function handleFeedback(e) {
    e.preventDefault();
    if (!feedbackBody.trim()) return;
    setBusy("feedback");
    setError("");
    try {
      await postFtcFeedback(subId, feedbackBody.trim(), activeField?.key);
      setFeedbackBody("");
      setActiveField(null);
      await loadSub();
      onDone?.();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  async function handleApprove() {
    setBusy("approve");
    setError("");
    try {
      await approveFtcSubmission(subId, approveNotes);
      await loadSub();
      onDone?.();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  async function handleSendMsg(e) {
    e.preventDefault();
    if (!msgBody.trim()) return;
    try {
      await postMessage(subId, msgBody.trim(), activeField?.key);
      const msgs = await fetchMessages(subId);
      setMessages(msgs);
      setMsgBody("");
      setActiveField(null);
    } catch (e) {
      setError(e.message);
    }
  }

  function handleFieldClick(key) {
    setActiveField(prev => prev?.key === key ? null : { key, label: fieldLabel(key) });
  }

  if (busy === "loading") return <div className="review-loading">Loading submission…</div>;
  if (!sub) return <div className="review-loading">Select a submission.</div>;

  const report        = sub.check_result || {};
  const parsed        = sub.card_parsed || {};
  const files         = sub.files || [];
  const commentedKeys = new Set(messages.map(m => m.field_ref).filter(Boolean));

  return (
    <div className="ftc-review">
      {error && <div className="notice notice-error">{error}</div>}

      <div className="review-header">
        <h3>{sub.card_ref || sub.card_filename}</h3>
        <div className="review-meta">
          <GateBadge gate={report.gate} />
          <span className={`status-badge badge-${sub.status}`}>{STATUS_LABEL[sub.status] || sub.status}</span>
          <span className="review-designer">by {sub.designer_display || sub.designer_username}</span>
        </div>
      </div>

      <div className="review-panels">
        {/* Left — card view */}
        <div className="review-raw">
          <div className="card-view-toolbar">
            <h4 style={{ margin: 0 }}>Cloth Card</h4>
            <div className="segmented">
              <button className={cardView === "raw" ? "active" : ""} onClick={() => setCardView("raw")}>Raw</button>
              <button className={cardView === "parsed" ? "active" : ""} onClick={() => setCardView("parsed")}>Parsed Fields</button>
            </div>
          </div>

          {cardView === "raw" ? (
            <pre className="raw-card" style={{ marginTop: 10 }}>{sub.card_raw_text}</pre>
          ) : (
            <div className="parsed-table" style={{ marginTop: 10 }}>
              {Object.entries(parsed)
                .filter(([, v]) => v !== null && v !== undefined && v !== "")
                .map(([key, val]) => (
                  <div
                    key={key}
                    className={`parsed-row parsed-row-clickable ${activeField?.key === key ? "parsed-row-active" : ""} ${commentedKeys.has(key) ? "parsed-row-commented" : ""}`}
                    onClick={() => handleFieldClick(key)}
                    title="Click to tag this field in your next message"
                  >
                    <span>{fieldLabel(key)}{commentedKeys.has(key) && <span className="comment-dot" title="Has comments"> ●</span>}</span>
                    <strong>{String(val)}</strong>
                  </div>
                ))}
            </div>
          )}

          {/* Attachments */}
          {files.length > 0 && (
            <div className="attachments-section" style={{ marginTop: 14 }}>
              <span className="section-label">Designer Attachments</span>
              <div className="attachment-list">
                {files.map(f => (
                  <a
                    key={f.id}
                    href={attachmentUrl(sub.id, f.filename)}
                    target="_blank"
                    rel="noreferrer"
                    className="attachment-item"
                  >
                    <span className="attachment-icon">{f.mime_type?.startsWith("image/") ? "🖼" : "📄"}</span>
                    <span className="attachment-name">{f.original_name}</span>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right — checks + actions */}
        <div className="review-checks">
          <h4>Check Results</h4>
          <p className="check-summary">
            {report.rules_run || 22} rules · {report.errors?.length || 0} errors · {report.warnings?.length || 0} warnings
          </p>

          {report.errors?.length > 0 && (
            <IssueList title="Errors" issues={report.errors} severity="error" />
          )}
          {report.warnings?.length > 0 && (
            <IssueList title="Warnings" issues={report.warnings} severity="warning" />
          )}
          {report.info?.length > 0 && (
            <IssueList title="Info" issues={report.info} severity="info" />
          )}

          {/* Message thread */}
          <div className="message-thread">
            <h4>Thread</h4>
            {messages.length === 0 && <p className="empty-hint">No messages.</p>}
            {messages.map((m) => (
              <div key={m.id} className={`message-row ${m.sender_role}`}>
                <span className="message-avatar">{m.sender_name[0]}</span>
                <div className="message-body">
                  <span className="message-sender">{m.sender_name}</span>
                  {m.field_ref && <span className="field-tag-badge">{fieldLabel(m.field_ref)}</span>}
                  <p>{m.body}</p>
                </div>
              </div>
            ))}

            {activeField && (
              <div className="field-tag-active">
                Tagging: <strong>{activeField.label}</strong>
                <button className="clear-tag-btn" onClick={() => setActiveField(null)}>✕</button>
              </div>
            )}

            <form className="message-compose" onSubmit={handleSendMsg}>
              <input
                type="text"
                placeholder={activeField ? `Comment on ${activeField.label}…` : "Message designer…"}
                value={msgBody}
                onChange={e => setMsgBody(e.target.value)}
              />
              <button className="btn btn-secondary btn-sm" type="submit" disabled={!msgBody.trim()}>
                Send
              </button>
            </form>
          </div>

          {/* FTC Actions */}
          {sub.status !== "approved" && (
            <div className="ftc-actions">
              <div className="ftc-action-section">
                <h4>Request Revision</h4>
                {activeField && (
                  <div className="field-tag-active">
                    Tagging: <strong>{activeField.label}</strong>
                    <button className="clear-tag-btn" onClick={() => setActiveField(null)}>✕</button>
                  </div>
                )}
                <form onSubmit={handleFeedback}>
                  <textarea
                    placeholder="Describe what needs to be corrected…"
                    value={feedbackBody}
                    onChange={e => setFeedbackBody(e.target.value)}
                    rows={3}
                    disabled={sub.status !== "submitted"}
                  />
                  <button
                    className="btn btn-secondary"
                    type="submit"
                    disabled={!feedbackBody.trim() || sub.status !== "submitted" || busy === "feedback"}
                  >
                    {busy === "feedback" ? "Sending…" : "Send Feedback"}
                  </button>
                </form>
              </div>

              {sub.status === "submitted" && (
                <div className="ftc-action-section ftc-approve-section">
                  <h4>Approve</h4>
                  <textarea
                    placeholder="Approval notes (optional)…"
                    value={approveNotes}
                    onChange={e => setApproveNotes(e.target.value)}
                    rows={2}
                  />
                  <button
                    className="btn btn-approve"
                    onClick={handleApprove}
                    disabled={busy === "approve"}
                  >
                    {busy === "approve" ? "Approving…" : "✓ Approve"}
                  </button>
                </div>
              )}
            </div>
          )}

          {sub.status === "approved" && sub.approval && (
            <div className="approval-badge">
              ✓ Approved by {sub.approval.ftc_member_name}
              <span className="approval-id">ID: {sub.approval.approval_id?.slice(0, 8).toUpperCase()}</span>
              <button className="btn btn-secondary btn-sm" onClick={() => onViewCert?.(sub.id)}>
                Print Certificate
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
