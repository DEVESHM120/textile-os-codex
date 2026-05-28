import { AlertCircle, AlertTriangle, Info } from "lucide-react";

const iconMap = {
  ERROR: AlertCircle,
  WARNING: AlertTriangle,
  INFO: Info,
};

export default function IssueList({ title, issues = [], emptyText }) {
  return (
    <section className="panel">
      <div className="panel-title">
        <h2>{title}</h2>
        <span>{issues.length}</span>
      </div>
      {issues.length === 0 ? (
        <p className="muted">{emptyText}</p>
      ) : (
        <div className="issue-list">
          {issues.map((issue, index) => {
            const Icon = iconMap[issue.severity] || Info;
            return (
              <article className={`issue issue-${issue.severity.toLowerCase()}`} key={`${issue.code}-${index}`}>
                <Icon size={18} />
                <div>
                  <strong>{issue.code}</strong>
                  <p>{issue.message}</p>
                  {issue.details?.action ? <small>{issue.details.action}</small> : null}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
