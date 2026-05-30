import { useEffect, useRef, useState } from "react";
import {
  fetchDesignerSubmissions,
  fetchDesignerSubmission,
  submitClothCard,
  recheckSubmission,
  reuploadClothCard,
  sendToFtc,
  fetchMessages,
  postMessage,
  uploadAttachment,
  attachmentUrl,
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

export default function DesignerDesk({ currentUser, onViewCert }) {
  const [submissions, setSubmissions] = useState([]);
  const [selected,    setSelected]    = useState(null);
  const [messages,    setMessages]    = useState([]);
  const [msgBody,     setMsgBody]     = useState("");
  const [note,        setNote]        = useState("");
  const [busy,        setBusy]        = useState("");
  const [error,       setError]       = useState("");
  const fileRef     = useRef(null);
  const reuploadRef = useRef(null);
  const attachRef   = useRef(null);

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
      const data = await fetchDesignerSubmission(sub.id);
      const msgs = await fetchMessages(sub.id);
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

  async function handleReupload(e) {
    const f = e.target.files?.[0];
    if (!selected || !f) return;
    setBusy("reupload");
    setError("");
    try {
      const data = await reuploadClothCard(selected.id, f);
      setSelected(data.submission);
      await loadList();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
      if (reuploadRef.current) reuploadRef.current.value = "";
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

  async function handleAttach(e) {
    const f = e.target.files?.[0];
    if (!selected || !f) return;
    setBusy("attach");
    setError("");
    try {
      const data = await uploadAttachment(selected.id, f);
      setSelected(prev => ({
        ...prev,
        files: [...(prev.files || []), data.file],
      }));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
      if (attachRef.current) attachRef.current.value = "";
    }
  }

  const report     = selected?.check_result || {};
  const gate       = report.gate || "UNKNOWN";
  const isEditable = selected && ["draft", "needs_revision"].includes(selected.status);
  const canSend    = selected && selected.status === "ready" && gate === "PASS";
  const canReupload = selected && gate !== "PASS" && isEditable;
  const files      = selected?.files || [];

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
            <input ref={fileRef} type="file" accept=".txt" style={{ display: "none" }} onChange={handleUpload} />
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
                    disabled={!isEditable || busy === "recheck"}
                  >
                    {busy === "recheck" ? "Rechecking…" : "Recheck"}
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={handleSend}
                    disabled={!canSend || busy === "send"}
                    title={!canSend ? "Only PASS cards can be sent to FTC" : ""}
                  >
                    {busy === "send" ? "Sending…" : "Send to FTC"}
                  </button>
                </div>
              </div>

              <div className="detail-status-row">
                <GateBadge gate={report.gate} />
                <StatusBadge status={selected.status} />
              </div>

              {/* Approved banner */}
              {selected.status === "approved" && (
                <div className="approval-banner">
                  <span>✓ Approved</span>
                  <button className="btn btn-secondary btn-sm" onClick={() => onViewCert?.(selected.id)}>
                    Print Certificate
                  </button>
                </div>
              )}

              {canReupload && (
                <div className="reupload-panel">
                  <div>
                    <strong>Corrected card required</strong>
                    <p>This card must PASS before it can be sent to FTC. Upload the corrected .txt card here.</p>
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => reuploadRef.current?.click()}
                    disabled={busy === "reupload"}
                  >
                    {busy === "reupload" ? "Uploading…" : "Re-upload Corrected Card"}
                  </button>
                  <input ref={reuploadRef} type="file" accept=".txt" style={{ display: "none" }} onChange={handleReupload} />
                </div>
              )}

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

              {/* Attachments */}
              <div className="attachments-section">
                <div className="attachments-header">
                  <span className="section-label">Attachments</span>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => attachRef.current?.click()}
                    disabled={busy === "attach"}
                  >
                    {busy === "attach" ? "Uploading…" : "+ Add File"}
                  </button>
                  <input
                    ref={attachRef}
                    type="file"
                    accept=".jpg,.jpeg,.png,.webp,.pdf"
                    style={{ display: "none" }}
                    onChange={handleAttach}
                  />
                </div>
                {files.length === 0 ? (
                  <p className="empty-hint" style={{ padding: "8px 0" }}>No attachments yet.</p>
                ) : (
                  <div className="attachment-list">
                    {files.map(f => (
                      <a
                        key={f.id}
                        href={attachmentUrl(selected.id, f.filename)}
                        target="_blank"
                        rel="noreferrer"
                        className="attachment-item"
                      >
                        <span className="attachment-icon">{f.mime_type?.startsWith("image/") ? "🖼" : "📄"}</span>
                        <span className="attachment-name">{f.original_name}</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>

              {/* Messages */}
              <div className="message-thread">
                <h4>FTC Thread</h4>
                {messages.length === 0 && <p className="empty-hint">No messages yet.</p>}
                {messages.map((m) => (
                  <div key={m.id} className={`message-row ${m.sender_role}`}>
                    <span className="message-avatar">{m.sender_name[0]}</span>
                    <div className="message-body">
                      <span className="message-sender">{m.sender_name}</span>
                      {m.field_ref && <span className="field-tag-badge">{m.field_ref.replace(/_/g, " ")}</span>}
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
