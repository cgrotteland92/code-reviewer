export interface Finding {
  severity: "HIGH" | "MEDIUM" | "LOW";
  title: string;
  description: string;
  location: string;
}

export interface AgentReport {
  agent_name: string;
  emoji: string;
  findings: Finding[];
  summary: string;
}

export interface CoordinatorSummary {
  overall_health: "CRITICAL" | "NEEDS_WORK" | "GOOD" | "EXCELLENT";
  critical_issues: string[];
  key_strengths: string[];
  recommended_actions: { priority: number; action: string }[];
  narrative: string;
}

export interface ReviewResult {
  reports: AgentReport[];
  coordinator: CoordinatorSummary;
}
