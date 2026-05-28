import { useEffect, useState } from "react";
import { fetchFtcInbox, fetchAllFtcSubmissions } from "../api/client.js";
import GateBadge from "../components/GateBadge.jsx";
import FtcReview from "./FtcReview.jsx";

const TABS = [
  { id: "pending",  label: "Pending Review",  fn: () => fetchFtcInbox()           },
  { id: "approved", label: "Approved",         fn: () => fetchFtcInbox("approved") },
  { id: "all",      label: "All",              fn: () => fetchAllFtcSubmissions()  },
];

const STATUS_LABEL = {
  draft:          "Draft",
  ready:          "Ready",
  submitted:      "Pending",
  needs_revision: "Needs Revision",
  approved:       "Approved",
};

function timeAgo(iso) {
  if (!iso) return "";
  const diff = (Date.now() - new Date(iso + "Z").getTime()) / 1000;
  if (diff < 60)  return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function FtcInbox({ currentUser }) {
  const [tab,        setTab]        = useState("pending");
  const [rows,       setRows]       = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState("");

  useEffect(() => { loadTab(tab); }, [tab]);

  async function loadTab(tabId) {
    setLoading(true);
    setError("");
    const tabDef = TABS.find(t => t.id === tabId);
    try {
      const data = await tabDef.fn();
      setRows(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleTabChange(tabId) {
    setTab(tabId);
    setSelectedId(null);
  }

  return (
    <div className="ftc-inbox">
      {error && <div className="notice notice-error">{error}</div>}

      {/* Tab bar */}
      <div className="inbox-tabs">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`inbox-tab ${tab === t.id ? "active" : ""}`}
            onClick={() => handleTabChange(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="inbox-layout">
        {/* Left — list */}
        <div className="inbox-list">
          {loading && <p className="empty-hint">Loading…</p>}
          {!loading && rows.length === 0 && (
            <p className="empty-hint">No submissions in this tab.</p>
          )}
          {rows.map((row) => (
            <div
              key={row.id}
              className={`queue-row ${selectedId === row.id ? "selected" : ""}`}
              onClick={() => setSelectedId(row.id)}
            >
              <div className="queue-row-top">
                <span className="queue-ref">{row.card_ref || row.card_filename}</span>
                <GateBadge gate={row.gate} />
              </div>
              <div className="queue-row-bottom">
                <span className={`status-badge badge-${row.status}`}>
                  {STATUS_LABEL[row.status] || row.status}
                </span>
                <span className="queue-meta">{row.designer_display} · {timeAgo(row.updated_at)}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right — review panel */}
        <div className="inbox-review">
          {selectedId ? (
            <FtcReview
              key={selectedId}
              subId={selectedId}
              currentUser={currentUser}
              onDone={() => loadTab(tab)}
            />
          ) : (
            <div className="detail-empty">Click a submission to review it.</div>
          )}
        </div>
      </div>
    </div>
  );
}
