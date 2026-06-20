"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { SyncButton } from "@/components/layout/sync-button";
import { InsightCard } from "@/components/cards/insight-card";
import { formatDuration, formatNumber, modelDisplayName } from "@/lib/utils";

function hourLabel(hour: number | null | undefined): string {
  if (hour === null || hour === undefined) return "—";
  const period = hour >= 12 ? "PM" : "AM";
  const h = hour % 12 || 12;
  return `${h}:00 ${period}`;
}

export default function InsightsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["insights"],
    queryFn: () => api.insights().then((r) => r.data),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">Productivity Insights</h1>
        <SyncButton />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <InsightCard
          label="Total Sessions"
          value={formatNumber(data?.total_sessions)}
          isLoading={isLoading}
        />
        <InsightCard
          label="Total Messages"
          value={formatNumber(data?.total_messages)}
          isLoading={isLoading}
        />
        <InsightCard
          label="Total Tool Calls"
          value={formatNumber(data?.total_tool_calls)}
          isLoading={isLoading}
        />
        <InsightCard
          label="Peak Day of Week"
          value={data?.peak_day_of_week}
          subtext="Most active coding day"
          isLoading={isLoading}
        />
        <InsightCard
          label="Most Active Hour"
          value={hourLabel(data?.most_active_hour)}
          subtext="When you code most"
          isLoading={isLoading}
        />
        <InsightCard
          label="Avg Session Duration"
          value={formatDuration(data?.avg_session_duration_minutes)}
          subtext="Per coding session"
          isLoading={isLoading}
        />
        <InsightCard
          label="Longest Session"
          value={formatDuration(data?.longest_session_duration_minutes)}
          subtext={data?.longest_session_id ? `Session ${data.longest_session_id.slice(0, 8)}` : undefined}
          isLoading={isLoading}
        />
        <InsightCard
          label="Avg Messages / Session"
          value={data?.avg_messages_per_session}
          isLoading={isLoading}
        />
        <InsightCard
          label="Most Used Tool"
          value={data?.most_used_tool}
          subtext={data?.most_used_tool_count ? `${data.most_used_tool_count.toLocaleString()} executions` : undefined}
          isLoading={isLoading}
        />
        <InsightCard
          label="Busiest Project"
          value={data?.busiest_project}
          subtext="Most sessions"
          isLoading={isLoading}
        />
        <InsightCard
          label="Cache Hit Rate"
          value={data?.cache_hit_rate !== undefined ? `${(data.cache_hit_rate * 100).toFixed(1)}%` : undefined}
          subtext="Prompt caching efficiency"
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
