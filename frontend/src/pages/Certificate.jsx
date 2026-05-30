import { useEffect, useState } from "react";
import { fetchCertificate } from "../api/client.js";

const FIELD_LABELS = {
  weave: "Weave", count_raw: "Count", warp_count: "Warp Count", weft_count: "Weft Count",
  grey_epi: "Grey EPI", fin_epi: "Finished EPI", grey_ppi: "Grey PPI", fin_ppi: "Finished PPI",
  gsm: "GSM", reed: "Reed", grey_width_inches: "Grey Width (in)", fin_width_inches: "Fin. Width (in)",
  fabric_composition: "Composition", loom_type: "Loom Type", customer: "Customer",
  season: "Season", pattern: "Pattern", shaft_count: "Shaft Count", body_ends: "Body Ends",
  total_ends: "Total Ends", selvedge_ends: "Selvedge Ends",
};

const SPEC_KEYS = [
  "count_raw","warp_count","weft_count","grey_epi","fin_epi","grey_ppi","fin_ppi",
  "gsm","reed","grey_width_inches","fin_width_inches","fabric_composition","loom_type",
  "body_ends","total_ends","shaft_count","selvedge_ends",
];

export default function Certificate({ subId, onBack }) {
  const [data,  setData]  = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchCertificate(subId)
      .then(setData)
      .catch(e => setError(e.message));
  }, [subId]);

  if (error) return (
    <div className="cert-page">
      <div className="cert-error">
        <p>Could not load certificate: {error}</p>
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
      </div>
    </div>
  );

  if (!data) return <div className="cert-page"><p className="cert-loading">Loading certificate…</p></div>;

  const { submission: sub, approval } = data;
  if (!approval) return (
    <div className="cert-page">
      <div className="cert-error">
        <p>This submission has not been approved yet.</p>
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
      </div>
    </div>
  );

  const parsed   = sub?.card_parsed || {};
  const report   = sub?.check_result || {};
  const specRows = SPEC_KEYS.filter(k => parsed[k] != null && parsed[k] !== "");
  const approvalShort = approval.approval_id?.slice(0, 8).toUpperCase();
  const approvedDate  = approval.approved_at ? new Date(approval.approved_at + "Z").toLocaleString() : "—";

  return (
    <div className="cert-page">
      <div className="cert-toolbar no-print">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn btn-primary" onClick={() => window.print()}>🖨 Print / Save PDF</button>
      </div>

      <div className="cert-sheet">
        <div className="cert-header">
          <div>
            <p className="cert-eyebrow">Textile OS · Feasibility Platform</p>
            <h1 className="cert-title">Fabric Feasibility Certificate</h1>
            <p className="cert-subtitle">Approved — Construction Verified</p>
          </div>
          <div className="cert-badge">✓ FTC VERIFIED</div>
        </div>

        <div className="cert-info-grid">
          <div className="cert-info-row"><span>Card Reference</span><strong>{sub?.card_ref || "—"}</strong></div>
          <div className="cert-info-row"><span>Weave</span><strong>{parsed.weave || "—"}</strong></div>
          <div className="cert-info-row"><span>Customer</span><strong>{parsed.customer || "—"}</strong></div>
          <div className="cert-info-row"><span>Season</span><strong>{parsed.season || "—"}</strong></div>
        </div>

        <div className="cert-section-title">Construction Specifications</div>
        <div className="cert-specs-grid">
          {specRows.map(k => (
            <div key={k} className="cert-spec-cell">
              <span>{FIELD_LABELS[k] || k}</span>
              <strong>{String(parsed[k])}</strong>
            </div>
          ))}
        </div>

        <div className="cert-check-summary">
          {report.rules_run || 22} feasibility rules checked ·{" "}
          {report.errors?.length || 0} errors · {report.warnings?.length || 0} warnings
        </div>

        <div className="cert-approval-block">
          <div className="cert-approval-details">
            <div className="cert-info-row"><span>Approved By</span><strong>{approval.ftc_member_name}</strong></div>
            <div className="cert-info-row"><span>Date &amp; Time</span><strong>{approvedDate}</strong></div>
            {approval.notes && <div className="cert-info-row"><span>Notes</span><strong>{approval.notes}</strong></div>}
            <div className="cert-info-row">
              <span>Approval ID</span>
              <strong className="cert-approval-id">{approvalShort}</strong>
            </div>
            <p className="cert-verify-hint">
              Verify at: {window.location.origin}/verify/{approval.approval_id}
            </p>
          </div>
          <div className="cert-watermark">APPROVED</div>
        </div>
      </div>
    </div>
  );
}
