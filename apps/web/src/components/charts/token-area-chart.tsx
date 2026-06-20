"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { DailyTokenPoint } from "@/types/api";
import { formatTokens } from "@/lib/utils";

interface TokenAreaChartProps {
  data: DailyTokenPoint[];
}

function formatXAxis(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function TokenAreaChart({ data }: TokenAreaChartProps) {
  if (!data?.length) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-zinc-600">
        No data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="inputGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="outputGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
        </defs>
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
          tickFormatter={(v) => formatTokens(v)}
          tick={{ fill: "#71717a", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={48}
        />
        <Tooltip
          contentStyle={{ backgroundColor: "#18181b", border: "1px solid #3f3f46", borderRadius: 6 }}
          labelStyle={{ color: "#a1a1aa", fontSize: 12 }}
          formatter={(v: number, name: string) => [
            formatTokens(v),
            name === "input_tokens" ? "Input" : name === "output_tokens" ? "Output" : name,
          ]}
          labelFormatter={formatXAxis}
        />
        <Area type="monotone" dataKey="input_tokens" stroke="#3b82f6" fill="url(#inputGrad)" strokeWidth={1.5} />
        <Area type="monotone" dataKey="output_tokens" stroke="#6366f1" fill="url(#outputGrad)" strokeWidth={1.5} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
