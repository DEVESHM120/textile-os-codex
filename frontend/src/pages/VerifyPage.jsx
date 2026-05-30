import { useEffect, useState } from "react";
import { fetchVerify } from "../api/client.js";

const FIELD_LABELS = {
  weave: "Weave", count_raw: "Count", gsm: "GSM", grey_epi: "Grey EPI",
  fabric_composition: "Composition", customer: "Customer", loom_type: "Loom Type",
  grey_width_inches: "Grey Width (in)", season: "Season",
};

export default function VerifyPage({ approvalId }) {
  const [data,  setData]  = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchVerify(approvalId)
      .then(setData)
      .catch(() => setError("Approval not found"));
  }, [approvalId]);

  if (!data && !error) return (
    <div className="verify-page">
      <div className="verify-card"><p style={{ color: "var(--muted)" }}>Verifying…</p></div>
    </div>
  );

  if (error) return (
    <div className="verify-page">
      <div className="verify-card verify-invalid">
        <div className="verify-header verify-header-fail">
          <span className="verify-icon">✗</span>
          <div>
            <h2>Invalid Approval Code</h2>
            <p>This approval ID was not found in the system.</p>
          </div>
        </div>
        <p className="verify-hint">The code may be incorrect or the record may have been removed.</p>
        <p className="verify-brand">Textile OS · Feasibility Platform</p>
      </div>
    </div>
  );

  const parsed      = data.card_parsed || {};
  const approvedAt  = data.approved_at ? new Date(data.approved_at + "Z").toLocaleString() : "—";
  const shortId     = data.approval_id?.slice(0, 8).toUpperCase();
  const specEntries = Object.entries(FIELD_LABELS).filter(([k]) => parsed[k] != null && parsed[k] !== "");

  return (
    <div className="verify-page">
      <div className="verify-card">
        <div className="verify-header verify-header-pass">
          <span className="verify-icon">✓</span>
          <div>
            <h2>Verified — FTC Approved</h2>
            <p className="verify-approval-id">{shortId}</p>
          </div>
        </div>

        <div className="verify-body">
          <div className="verify-table">
            <div className="verify-row"><span>Card Reference</span><strong>{data.card_ref}</strong></div>
            <div className="verify-row"><span>Approved By</span><strong>{data.ftc_member_name}</strong></div>
            <div className="verify-row"><span>Approved On</span><strong>{approvedAt}</strong></div>
            <div className="verify-row"><span>Designer</span><strong>{data.designer_name}</strong></div>
            {data.notes && <div className="verify-row"><span>Notes</span><strong>{data.notes}</strong></div>}
          </div>

          {specEntries.length > 0 && (
            <>
              <p className="verify-section-title">Fabric Specifications</p>
              <div className="verify-specs">
                {specEntries.map(([k, label]) => (
                  <div key={k} className="verify-spec-cell">
                    <span>{label}</span>
                    <strong>{String(parsed[k])}</strong>
                  </div>
                ))}
              </div>
            </>
          )}

          <p className="verify-full-id">Full ID: {data.approval_id}</p>
        </div>

        <p className="verify-brand">Textile OS · Feasibility Platform</p>
      </div>
    </div>
  );
}
