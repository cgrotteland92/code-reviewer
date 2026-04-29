import { AgentReport, Finding } from "@/lib/types";
import { Badge } from "@/components/ui/badge";

const SEVERITY_STYLES: Record<
  string,
  { badge: string; section: string }
> = {
  HIGH: {
    badge: "bg-red-950 text-red-400 border-red-800",
    section: "text-red-400",
  },
  MEDIUM: {
    badge: "bg-yellow-950 text-yellow-400 border-yellow-800",
    section: "text-yellow-400",
  },
  LOW: {
    badge: "bg-blue-950 text-blue-400 border-blue-800",
    section: "text-blue-400",
  },
};

function FindingCard({ finding }: { finding: Finding }) {
  const styles = SEVERITY_STYLES[finding.severity] ?? SEVERITY_STYLES.LOW;
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 space-y-2">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge
          variant="outline"
          className={`text-xs font-mono shrink-0 ${styles.badge}`}
        >
          {finding.severity}
        </Badge>
        <span className="font-medium text-zinc-100 text-sm">
          {finding.title}
        </span>
      </div>
      {finding.location && (
        <div className="text-xs text-zinc-500 font-mono">
          📍 {finding.location}
        </div>
      )}
      <p className="text-sm text-zinc-300 leading-relaxed">
        {finding.description}
      </p>
    </div>
  );
}

interface Props {
  report: AgentReport;
}

export function AgentTab({ report }: Props) {
  return (
    <div className="space-y-5 pt-4">
      {report.summary && (
        <p className="text-sm text-zinc-400 italic">{report.summary}</p>
      )}

      {report.findings.length === 0 && (
        <div className="bg-green-950 border border-green-800 rounded-lg p-4 text-green-400 text-sm">
          No {report.agent_name.toLowerCase()} findings detected.
        </div>
      )}

      {(["HIGH", "MEDIUM", "LOW"] as const).map((sev) => {
        const bucket = report.findings.filter((f) => f.severity === sev);
        if (!bucket.length) return null;
        const styles = SEVERITY_STYLES[sev];
        return (
          <div key={sev} className="space-y-3">
            <h3
              className={`text-xs font-semibold uppercase tracking-widest ${styles.section}`}
            >
              {sev} &mdash; {bucket.length} finding
              {bucket.length !== 1 ? "s" : ""}
            </h3>
            {bucket.map((f, i) => (
              <FindingCard key={i} finding={f} />
            ))}
          </div>
        );
      })}
    </div>
  );
}
