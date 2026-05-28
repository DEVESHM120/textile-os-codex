import { useEffect, useState } from "react";
import {
  fetchFtcSubmission,
  fetchMessages,
  postFtcFeedback,
  approveFtcSubmission,
  postMessage,
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

export default function FtcReview({ subId, currentUser, onDone }) {
  const [sub,          setSub]          = useState(null);
  const [messages,     setMessages]     = useState([]);
  const [feedbackBody, setFeedbackBody] = useState("");
  const [approveNotes, setApproveNotes] = useState("");
  const [msgBody,      setMsgBody]      = useState("");
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
      await postFtcFeedback(subId, feedbackBody.trim());
      setFeedbackBody("");
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
      await postMessage(subId, msgBody.trim());
      const msgs = await fetchMessages(subId);
      setMessages(msgs);
      setMsgBody("");
    } catch (e) {
      setError(e.message);
    }
  }

  if (busy === "loading") return <div className="review-loading">Loading submission…</div>;
  if (!sub) return <div className="review-loading">Select a submission.</div>;

  const report = sub.check_result || {};

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
        {/* Left — raw card */}
        <div className="review-raw">
          <h4>Raw Cloth Card</h4>
          <pre className="raw-card">{sub.card_raw_text}</pre>
        </div>

        {/* Right — issues + actions */}
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
                  <p>{m.body}</p>
                </div>
              </div>
            ))}
            <form className="message-compose" onSubmit={handleSendMsg}>
              <input
                type="text"
                placeholder="Message designer…"
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
              <span className="approval-id">ID: {sub.approval.approval_id?.slice(0, 8)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
