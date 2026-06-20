"use client";

import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useStore } from "@/lib/store";
import { MetricCard } from "@/components/cards/metric-card";
import { TokenAreaChart } from "@/components/charts/token-area-chart";
import { CostBarChart } from "@/components/charts/cost-bar-chart";
import { SyncButton } from "@/components/layout/sync-button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatTokens, formatCost, formatNumber, modelDisplayName } from "@/lib/utils";

export default function OverviewPage() {
  const { lastSyncAt, setLastSyncAt, setIsSyncing } = useStore();
  const queryClient = useQueryClient();

  const { data: overview, isLoading } = useQuery({
    queryKey: ["overview"],
    queryFn: () => api.overview().then((r) => r.data),
  });

  // Auto-sync once on first open
  useEffect(() => {
    if (!lastSyncAt) {
      setIsSyncing(true);
      api
        .sync()
        .then(() => {
          setLastSyncAt(new Date());
          queryClient.invalidateQueries();
        })
        .finally(() => setIsSyncing(false));
    }
  }, []); // eslint-disable-line

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-zinc-100">Overview</h1>
          {lastSyncAt && (
            <p className="text-xs text-zinc-500 mt-0.5">
              Last synced {lastSyncAt.toLocaleTimeString()}
            </p>
          )}
        </div>
        <SyncButton />
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard
          title="Total Sessions"
          value={formatNumber(overview?.total_sessions)}
          isLoading={isLoading}
        />
        <MetricCard
          title="Total Tokens"
          value={formatTokens(overview?.total_tokens)}
          sub="all time"
          isLoading={isLoading}
        />
        <MetricCard
          title="Cost (30 days)"
          value={formatCost(overview?.cost_30d)}
          sub={`${formatCost(overview?.cost_all_time)} all time`}
          isLoading={isLoading}
        />
        <MetricCard
          title="Active Projects"
          value={overview?.active_projects_30d}
          sub={`${overview?.total_projects ?? "—"} total`}
          isLoading={isLoading}
        />
      </div>

      {/* Highlights */}
      {(overview?.most_active_project || overview?.most_used_model) && (
        <div className="flex gap-3 flex-wrap">
          {overview.most_active_project && (
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <span className="text-zinc-600">Most active</span>
              <Badge variant="outline">{overview.most_active_project}</Badge>
            </div>
          )}
          {overview.most_used_model && (
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <span className="text-zinc-600">Primary model</span>
              <Badge variant="blue">{modelDisplayName(overview.most_used_model)}</Badge>
            </div>
          )}
        </div>
      )}

      {/* Charts */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Token Usage — 30 days</CardTitle>
          </CardHeader>
          <CardContent>
            <TokenAreaChart data={overview?.token_trend ?? []} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily Cost — 30 days</CardTitle>
          </CardHeader>
          <CardContent>
            <CostBarChart data={overview?.cost_trend ?? []} />
          </CardContent>
        </Card>
      </div>

      {/* Token breakdown */}
      {overview && (
        <Card>
          <CardHeader>
            <CardTitle>Token Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div>
                <p className="text-xs text-zinc-500">Input</p>
                <p className="text-base font-medium text-zinc-100 mt-0.5">
                  {formatTokens(overview.total_input_tokens)}
                </p>
              </div>
              <div>
                <p className="text-xs text-zinc-500">Output</p>
                <p className="text-base font-medium text-zinc-100 mt-0.5">
                  {formatTokens(overview.total_output_tokens)}
                </p>
              </div>
              <div>
                <p className="text-xs text-zinc-500">Cache</p>
                <p className="text-base font-medium text-zinc-100 mt-0.5">
                  {formatTokens(overview.total_cache_tokens)}
                </p>
              </div>
              <div>
                <p className="text-xs text-zinc-500">Lifetime Cost</p>
                <p className="text-base font-medium text-zinc-100 mt-0.5">
                  {formatCost(overview.cost_all_time)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
