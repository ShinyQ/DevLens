"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { api } from "@/lib/api";
import { SyncButton } from "@/components/layout/sync-button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCost, formatTokens, modelDisplayName, cn } from "@/lib/utils";
import type { CostsParams } from "@/types/api";

type Granularity = "day" | "week" | "month";

export default function CostsPage() {
  const [granularity, setGranularity] = useState<Granularity>("day");
  const [days, setDays] = useState(30);

  const params: CostsParams = { granularity, days };

  const { data, isLoading } = useQuery({
    queryKey: ["costs", params],
    queryFn: () => api.costs(params).then((r) => r.data),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">Cost Analytics</h1>
        <SyncButton />
      </div>

      {/* Controls */}
      <div className="flex gap-3 flex-wrap">
        <div className="flex rounded-md border border-zinc-700 overflow-hidden">
          {(["day", "week", "month"] as Granularity[]).map((g) => (
            <button
              key={g}
              className={cn(
                "px-3 py-1.5 text-xs capitalize transition-colors",
                granularity === g
                  ? "bg-zinc-700 text-zinc-100"
                  : "text-zinc-400 hover:text-zinc-200"
              )}
              onClick={() => setGranularity(g)}
            >
              {g}
            </button>
          ))}
        </div>
        <div className="flex rounded-md border border-zinc-700 overflow-hidden">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              className={cn(
                "px-3 py-1.5 text-xs transition-colors",
                days === d ? "bg-zinc-700 text-zinc-100" : "text-zinc-400 hover:text-zinc-200"
              )}
              onClick={() => setDays(d)}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Total Cost", value: data?.total_cost },
          { label: "Input Cost", value: data?.total_input_cost },
          { label: "Output Cost", value: data?.total_output_cost },
          { label: "Cache Cost", value: data?.total_cache_cost },
        ].map(({ label, value }) => (
          <Card key={label}>
            <CardContent className="pt-4">
              <p className="text-xs text-zinc-500">{label}</p>
              {isLoading ? (
                <Skeleton className="h-7 w-20 mt-1" />
              ) : (
                <p className="text-xl font-semibold text-zinc-100 mt-0.5">{formatCost(value)}</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Stacked bar chart */}
      <Card>
        <CardHeader>
          <CardTitle>Cost Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-64 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={data?.data_points ?? []} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis
                  dataKey="period"
                  tick={{ fill: "#71717a", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tickFormatter={(v) => formatCost(v)}
                  tick={{ fill: "#71717a", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  width={60}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: "#18181b", border: "1px solid #3f3f46", borderRadius: 6 }}
                  labelStyle={{ color: "#a1a1aa", fontSize: 12 }}
                  formatter={(v: number, name: string) => [
                    formatCost(v),
                    name === "input_cost" ? "Input" : name === "output_cost" ? "Output" : "Cache",
                  ]}
                />
                <Bar dataKey="input_cost" stackId="a" fill="#3b82f6" />
                <Bar dataKey="output_cost" stackId="a" fill="#6366f1" />
                <Bar dataKey="cache_cost" stackId="a" fill="#8b5cf6" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Model breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Cost by Model</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-zinc-800 overflow-hidden">
            <table className="w-full text-left">
              <thead className="border-b border-zinc-800 bg-zinc-900/50">
                <tr>
                  {["Model", "Input Tokens", "Output Tokens", "Est. Cost", "Share"].map((h) => (
                    <th key={h} className="px-4 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {isLoading
                  ? Array.from({ length: 3 }).map((_, i) => (
                      <tr key={i}>
                        {Array.from({ length: 5 }).map((_, j) => (
                          <td key={j} className="px-4 py-3">
                            <Skeleton className="h-4 w-16" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : (data?.model_breakdown ?? []).map((m) => (
                      <tr key={m.model} className="hover:bg-zinc-800/20">
                        <td className="px-4 py-3">
                          <span className="text-sm text-zinc-200">{modelDisplayName(m.model)}</span>
                          <p className="text-[10px] text-zinc-600 font-mono">{m.model}</p>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm text-zinc-300">{formatTokens(m.input_tokens)}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm text-zinc-300">{formatTokens(m.output_tokens)}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm text-zinc-100 font-medium">{formatCost(m.estimated_cost)}</span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-zinc-800 rounded-full h-1.5 max-w-[80px]">
                              <div
                                className="bg-blue-500 h-1.5 rounded-full"
                                style={{ width: `${m.percentage}%` }}
                              />
                            </div>
                            <span className="text-xs text-zinc-400">{m.percentage}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
