import { CoordinatorSummary } from "@/lib/types";

const HEALTH_CONFIG: Record<
  string,
  { icon: string; label: string; color: string }
> = {
  CRITICAL: { icon: "🚨", label: "CRITICAL", color: "text-red-400" },
  NEEDS_WORK: { icon: "⚠️", label: "NEEDS WORK", color: "text-yellow-400" },
  GOOD: { icon: "✅", label: "GOOD", color: "text-green-400" },
  EXCELLENT: { icon: "⭐", label: "EXCELLENT", color: "text-blue-400" },
};

interface Props {
  coordinator: CoordinatorSummary;
}

export function SummaryTab({ coordinator }: Props) {
  const health =
    HEALTH_CONFIG[coordinator.overall_health] ?? HEALTH_CONFIG.NEEDS_WORK;
  const actions = [...coordinator.recommended_actions].sort(
    (a, b) => a.priority - b.priority
  );

  return (
    <div className="space-y-5 pt-4">
      <h2 className="text-xl font-bold">
        {health.icon} Overall Health:{" "}
        <span className={health.color}>{health.label}</span>
      </h2>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <h3 className="text-xs font-semibold uppercase tracking-widest text-red-400 mb-3">
            🚨 Critical Issues
          </h3>
          {coordinator.critical_issues.length ? (
            <ul className="space-y-1.5">
              {coordinator.critical_issues.map((issue, i) => (
                <li key={i} className="text-sm text-zinc-300 flex gap-2">
                  <span className="text-zinc-600 shrink-0">·</span>
                  {issue}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-green-400">
              No critical issues identified.
            </p>
          )}
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <h3 className="text-xs font-semibold uppercase tracking-widest text-green-400 mb-3">
            ✅ Key Strengths
          </h3>
          {coordinator.key_strengths?.length ? (
            <ul className="space-y-1.5">
              {coordinator.key_strengths.map((s, i) => (
                <li key={i} className="text-sm text-zinc-300 flex gap-2">
                  <span className="text-zinc-600 shrink-0">·</span>
                  {s}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-zinc-500">No specific strengths noted.</p>
          )}
        </div>
      </div>

      {actions.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <h3 className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">
            📋 Recommended Actions
          </h3>
          <ol className="space-y-2">
            {actions.map((a, i) => (
              <li key={i} className="text-sm text-zinc-300 flex gap-3">
                <span className="text-zinc-500 font-mono shrink-0">
                  {a.priority}.
                </span>
                <span>{a.action}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {coordinator.narrative && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <h3 className="text-xs font-semibold uppercase tracking-widest text-zinc-400 mb-3">
            📝 Analysis
          </h3>
          <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
            {coordinator.narrative}
          </div>
        </div>
      )}
    </div>
  );
}
