import { useEffect, useRef, useState } from "react";
import {
  fetchDesignerSubmissions,
  fetchDesignerSubmission,
  submitClothCard,
  recheckSubmission,
  sendToFtc,
  fetchMessages,
  postMessage,
} from "../api/client.js";
import GateBadge from "../components/GateBadge.jsx";
import IssueList from "../components/IssueList.jsx";

const STATUS_LABEL = {
  draft:          "Draft",
  ready:          "Ready",
  submitted:      "With FTC",
  needs_revision: "Needs Revision",
  approved:       "Approved",
};

function StatusBadge({ status }) {
  const cls = {
    draft:          "badge-draft",
    ready:          "badge-ready",
    submitted:      "badge-submitted",
    needs_revision: "badge-revision",
    approved:       "badge-approved",
  }[status] || "";
  return <span className={`status-badge ${cls}`}>{STATUS_LABEL[status] || status}</span>;
}

export default function DesignerDesk({ currentUser }) {
  const [submissions, setSubmissions] = useState([]);
  const [selected,    setSelected]    = useState(null);
  const [messages,    setMessages]    = useState([]);
  const [msgBody,     setMsgBody]     = useState("");
  const [note,        setNote]        = useState("");
  const [busy,        setBusy]        = useState("");
  const [error,       setError]       = useState("");
  const fileRef = useRef(null);

  useEffect(() => { loadList(); }, []);

  async function loadList() {
    try {
      const rows = await fetchDesignerSubmissions();
      setSubmissions(rows);
    } catch (e) {
      setError(e.message);
    }
  }

  async function selectSub(sub) {
    setBusy("loading");
    try {
      const data  = await fetchDesignerSubmission(sub.id);
      const msgs  = await fetchMessages(sub.id);
      setSelected(data);
      setMessages(msgs);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  async function handleUpload(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    setBusy("submit");
    setError("");
    try {
      const data = await submitClothCard({ file: f });
      await loadList();
      await selectSub(data.submission);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleRecheck() {
    if (!selected) return;
    setBusy("recheck");
    setError("");
    try {
      const data = await recheckSubmission(selected.id);
      setSelected(data.submission);
      await loadList();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  async function handleSend() {
    if (!selected) return;
    setBusy("send");
    setError("");
    try {
      await sendToFtc(selected.id, note);
      const data = await fetchDesignerSubmission(selected.id);
      setSelected(data);
      await loadList();
      setNote("");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  async function handleSendMsg(e) {
    e.preventDefault();
    if (!selected || !msgBody.trim()) return;
    try {
      await postMessage(selected.id, msgBody.trim());
      const msgs = await fetchMessages(selected.id);
      setMessages(msgs);
      setMsgBody("");
    } catch (e) {
      setError(e.message);
    }
  }

  const canSend = selected && ["ready", "needs_revision"].includes(selected.status);
  const report  = selected?.check_result || {};

  return (
    <div className="designer-desk">
      {error && <div className="notice notice-error">{error}</div>}

      <div className="desk-layout">
        {/* Left: queue */}
        <div className="desk-queue">
          <div className="desk-queue-header">
            <h3>My Submissions</h3>
            <button
              className="btn btn-primary btn-sm"
              onClick={() => fileRef.current?.click()}
              disabled={busy === "submit"}
            >
              {busy === "submit" ? "Uploading…" : "+ Upload Card"}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".txt"
              style={{ display: "none" }}
              onChange={handleUpload}
            />
          </div>

          {submissions.length === 0 && (
            <p className="empty-hint">No submissions yet. Upload a .txt cloth card.</p>
          )}

          {submissions.map((sub) => (
            <div
              key={sub.id}
              className={`queue-row ${selected?.id === sub.id ? "selected" : ""}`}
              onClick={() => selectSub(sub)}
            >
              <div className="queue-row-top">
                <span className="queue-ref">{sub.card_ref || sub.card_filename}</span>
                <GateBadge gate={sub.gate} />
              </div>
              <div className="queue-row-bottom">
                <StatusBadge status={sub.status} />
                <span className="queue-meta">{sub.n_errors}E · {sub.n_warnings}W</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right: detail */}
        <div className="desk-detail">
          {!selected ? (
            <div className="detail-empty">Select a submission or upload a new cloth card.</div>
          ) : (
            <>
              <div className="detail-header">
                <h3>{selected.card_ref || selected.card_filename}</h3>
                <div className="detail-actions">
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={handleRecheck}
                    disabled={busy === "recheck"}
                  >
                    {busy === "recheck" ? "Rechecking…" : "Recheck"}
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={handleSend}
                    disabled={!canSend || busy === "send"}
                    title={!canSend ? `Cannot send from status: ${selected.status}` : ""}
                  >
                    {busy === "send" ? "Sending…" : "Send to FTC"}
                  </button>
                </div>
              </div>

              <div className="detail-status-row">
                <GateBadge gate={report.gate} />
                <StatusBadge status={selected.status} />
              </div>

              {canSend && (
                <div className="detail-note">
                  <textarea
                    placeholder="Optional note to FTC…"
                    value={note}
                    onChange={e => setNote(e.target.value)}
                    rows={2}
                  />
                </div>
              )}

              {/* Raw card */}
              <details className="raw-card-details">
                <summary>Raw card text</summary>
                <pre className="raw-card">{selected.card_raw_text}</pre>
              </details>

              {/* Issues */}
              {report.errors?.length > 0 && (
                <IssueList title="Errors" issues={report.errors} severity="error" />
              )}
              {report.warnings?.length > 0 && (
                <IssueList title="Warnings" issues={report.warnings} severity="warning" />
              )}

              {/* Messages */}
              <div className="message-thread">
                <h4>FTC Thread</h4>
                {messages.length === 0 && (
                  <p className="empty-hint">No messages yet.</p>
                )}
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
                    placeholder="Write a message…"
                    value={msgBody}
                    onChange={e => setMsgBody(e.target.value)}
                  />
                  <button className="btn btn-primary btn-sm" type="submit" disabled={!msgBody.trim()}>
                    Send
                  </button>
                </form>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
