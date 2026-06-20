"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { SyncButton } from "@/components/layout/sync-button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ToolUsageChart } from "@/components/charts/tool-usage-chart";
import { cn } from "@/lib/utils";

export default function ToolsPage() {
  const { data: tools = [], isLoading } = useQuery({
    queryKey: ["tools"],
    queryFn: () => api.tools().then((r) => r.data),
  });

  const totalCalls = tools.reduce((s, t) => s + t.execution_count, 0);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">Tool Analytics</h1>
        <SyncButton />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top Tools by Usage</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : (
              <ToolUsageChart data={tools} />
            )}
          </CardContent>
        </Card>

        {/* Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-xs text-zinc-500">Total Tool Calls</p>
              <p className="text-2xl font-semibold text-zinc-100 mt-0.5">{totalCalls.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Unique Tools</p>
              <p className="text-2xl font-semibold text-zinc-100 mt-0.5">{tools.length}</p>
            </div>
            {tools[0] && (
              <div>
                <p className="text-xs text-zinc-500">Most Used</p>
                <p className="text-base font-medium text-zinc-100 mt-0.5 font-mono">{tools[0].tool_name}</p>
                <p className="text-xs text-zinc-500">{tools[0].execution_count.toLocaleString()} executions</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-zinc-800 overflow-hidden">
        <table className="w-full text-left">
          <thead className="border-b border-zinc-800 bg-zinc-900/50">
            <tr>
              {["Tool", "Executions", "Errors", "Error Rate", "Sessions"].map((h) => (
                <th key={h} className="px-4 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {isLoading
              ? Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 5 }).map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <Skeleton className="h-4 w-20" />
                      </td>
                    ))}
                  </tr>
                ))
              : tools.map((t) => (
                  <tr key={t.tool_name} className="hover:bg-zinc-800/20">
                    <td className="px-4 py-3">
                      <span className="text-sm font-mono text-zinc-200">{t.tool_name}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-300">{t.execution_count.toLocaleString()}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-400">{t.is_error_count}</span>
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        variant={t.error_rate > 15 ? "red" : t.error_rate > 5 ? "yellow" : "green"}
                      >
                        {t.error_rate}%
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-400">{t.session_count}</span>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
        {!isLoading && tools.length === 0 && (
          <div className="py-16 text-center text-sm text-zinc-600">No tool usage data yet.</div>
        )}
      </div>
    </div>
  );
}
