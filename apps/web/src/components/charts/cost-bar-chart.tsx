"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { DailyCostPoint } from "@/types/api";
import { formatCost } from "@/lib/utils";

interface CostBarChartProps {
  data: DailyCostPoint[];
}

function formatXAxis(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function CostBarChart({ data }: CostBarChartProps) {
  if (!data?.length) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-zinc-600">
        No data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
        <XAxis
          dataKey="date"
          tickFormatter={formatXAxis}
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
          width={56}
        />
        <Tooltip
          contentStyle={{ backgroundColor: "#18181b", border: "1px solid #3f3f46", borderRadius: 6 }}
          labelStyle={{ color: "#a1a1aa", fontSize: 12 }}
          formatter={(v: number, name: string) => [
            formatCost(v),
            name === "input_cost" ? "Input" : name === "output_cost" ? "Output" : "Cache",
          ]}
          labelFormatter={formatXAxis}
        />
        <Bar dataKey="input_cost" stackId="a" fill="#3b82f6" radius={[0, 0, 0, 0]} />
        <Bar dataKey="output_cost" stackId="a" fill="#6366f1" radius={[0, 0, 0, 0]} />
        <Bar dataKey="cache_cost" stackId="a" fill="#8b5cf6" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
