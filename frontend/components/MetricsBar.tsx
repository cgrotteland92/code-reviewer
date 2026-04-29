import { Finding } from "@/lib/types";

const HEALTH_STYLES: Record<string, string> = {
  CRITICAL: "text-red-400",
  NEEDS_WORK: "text-yellow-400",
  GOOD: "text-green-400",
  EXCELLENT: "text-blue-400",
};

const HEALTH_LABELS: Record<string, string> = {
  CRITICAL: "CRITICAL",
  NEEDS_WORK: "NEEDS WORK",
  GOOD: "GOOD",
  EXCELLENT: "EXCELLENT",
};

interface Props {
  findings: Finding[];
  health: string;
}

export function MetricsBar({ findings, health }: Props) {
  const high = findings.filter((f) => f.severity === "HIGH").length;
  const medium = findings.filter((f) => f.severity === "MEDIUM").length;
  const low = findings.filter((f) => f.severity === "LOW").length;

  const metrics = [
    { label: "Total Findings", value: findings.length, color: "text-zinc-100" },
    { label: "High", value: high, color: "text-red-400" },
    { label: "Medium", value: medium, color: "text-yellow-400" },
    { label: "Low", value: low, color: "text-blue-400" },
    {
      label: "Health",
      value: HEALTH_LABELS[health] ?? health,
      color: HEALTH_STYLES[health] ?? "text-zinc-400",
    },
  ];

  return (
    <div className="grid grid-cols-5 gap-3">
      {metrics.map(({ label, value, color }) => (
        <div
          key={label}
          className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 text-center"
        >
          <div className={`text-2xl font-bold ${color}`}>{value}</div>
          <div className="text-xs text-zinc-500 mt-1">{label}</div>
        </div>
      ))}
    </div>
  );
}
