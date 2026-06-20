"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { ToolStat } from "@/types/api";

interface ToolUsageChartProps {
  data: ToolStat[];
}

export function ToolUsageChart({ data }: ToolUsageChartProps) {
  const top20 = data.slice(0, 20);

  if (!top20.length) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-zinc-600">
        No tool usage data
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(240, top20.length * 28)}>
      <BarChart
        data={top20}
        layout="vertical"
        margin={{ top: 4, right: 16, left: 4, bottom: 4 }}
      >
        <XAxis
          type="number"
          tick={{ fill: "#71717a", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="tool_name"
          width={80}
          tick={{ fill: "#a1a1aa", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{ backgroundColor: "#18181b", border: "1px solid #3f3f46", borderRadius: 6 }}
          labelStyle={{ color: "#a1a1aa", fontSize: 12 }}
          formatter={(v: number) => [v.toLocaleString(), "Executions"]}
        />
        <Bar dataKey="execution_count" radius={[0, 3, 3, 0]}>
          {top20.map((entry, idx) => (
            <Cell key={idx} fill={entry.error_rate > 15 ? "#ef4444" : entry.error_rate > 5 ? "#eab308" : "#3b82f6"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
