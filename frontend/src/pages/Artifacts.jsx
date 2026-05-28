import { Download } from "lucide-react";
import { artifactDownloadUrl } from "../api/client.js";

export default function Artifacts({ workflow, latestArtifact }) {
  const artifacts = latestArtifact
    ? [latestArtifact, ...(workflow?.artifacts || []).filter((item) => item.id !== latestArtifact.id)]
    : workflow?.artifacts || [];

  return (
    <section className="panel">
      <div className="panel-title">
        <h2>Artifacts</h2>
        <span>{artifacts.length}</span>
      </div>
      <div className="artifact-list">
        {artifacts.length === 0 ? <p className="muted">No generated files yet.</p> : null}
        {artifacts.map((artifact) => (
          <a
            key={artifact.id || artifact.filename}
            className="artifact-row"
            href={artifactDownloadUrl(artifact.download_url || `/api/artifacts/${artifact.id}/download`)}
            download
          >
            <Download size={18} />
            <div>
              <strong>{artifact.filename}</strong>
              <span>{artifact.artifact_type || "label_workbook"}</span>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}
