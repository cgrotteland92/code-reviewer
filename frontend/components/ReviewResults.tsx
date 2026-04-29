import { ReviewResult } from "@/lib/types";
import { MetricsBar } from "@/components/MetricsBar";
import { AgentTab } from "@/components/AgentTab";
import { SummaryTab } from "@/components/SummaryTab";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

function tabLabel(report: ReviewResult["reports"][number]): string {
  const total = report.findings.length;
  const high = report.findings.filter((f) => f.severity === "HIGH").length;
  if (total === 0) return `${report.emoji} ${report.agent_name}`;
  if (high)
    return `${report.emoji} ${report.agent_name} (${total} · ${high} HIGH)`;
  return `${report.emoji} ${report.agent_name} (${total})`;
}

interface Props {
  result: ReviewResult;
}

export function ReviewResults({ result }: Props) {
  const allFindings = result.reports.flatMap((r) => r.findings);

  return (
    <div className="space-y-4">
      <div className="border-t border-zinc-800 pt-4">
        <MetricsBar
          findings={allFindings}
          health={result.coordinator.overall_health}
        />
      </div>

      <Tabs defaultValue="0">
        <TabsList className="h-auto flex-wrap gap-1 w-full justify-start">
          {result.reports.map((r, i) => (
            <TabsTrigger key={i} value={String(i)} className="text-xs">
              {tabLabel(r)}
            </TabsTrigger>
          ))}
          <TabsTrigger value="summary" className="text-xs">
            🎯 Summary
          </TabsTrigger>
        </TabsList>

        {result.reports.map((r, i) => (
          <TabsContent key={i} value={String(i)}>
            <AgentTab report={r} />
          </TabsContent>
        ))}

        <TabsContent value="summary">
          <SummaryTab coordinator={result.coordinator} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
