import { AlertTriangle, CheckCircle2, CircleAlert } from "lucide-react";

export default function GateBadge({ gate = "UNKNOWN" }) {
  const normalized = gate || "UNKNOWN";
  const Icon = normalized === "PASS" ? CheckCircle2 : normalized === "ERROR" ? CircleAlert : AlertTriangle;
  return (
    <span className={`gate gate-${normalized.toLowerCase()}`}>
      <Icon size={16} />
      {normalized}
    </span>
  );
}
