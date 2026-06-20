"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Cpu, User } from "lucide-react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  formatTokens,
  formatCost,
  formatDateTime,
  formatDuration,
  modelDisplayName,
} from "@/lib/utils";

export default function SessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = parseInt(params.id as string);

  const { data: session, isLoading } = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => api.session(sessionId).then((r) => r.data),
    enabled: !isNaN(sessionId),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <h1 className="text-lg font-semibold text-zinc-100">Session Detail</h1>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      ) : session ? (
        <>
          {/* Session metadata */}
          <Card>
            <CardContent className="pt-4">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div>
                  <p className="text-xs text-zinc-500">Project</p>
                  <p className="text-sm font-medium text-zinc-100 mt-0.5">{session.project_name}</p>
                </div>
                <div>
                  <p className="text-xs text-zinc-500">Model</p>
                  <div className="mt-0.5">
                    {session.model ? (
                      <Badge variant="blue">{modelDisplayName(session.model)}</Badge>
                    ) : (
                      <span className="text-zinc-600">—</span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-xs text-zinc-500">Duration</p>
                  <p className="text-sm font-medium text-zinc-100 mt-0.5">
                    {formatDuration(session.duration_minutes)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-zinc-500">Cost</p>
                  <p className="text-sm font-medium text-zinc-100 mt-0.5">
                    {formatCost(session.estimated_cost)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-zinc-500">Messages</p>
                  <p className="text-sm font-medium text-zinc-100 mt-0.5">{session.message_count}</p>
                </div>
                <div>
                  <p className="text-xs text-zinc-500">Tool Calls</p>
                  <p className="text-sm font-medium text-zinc-100 mt-0.5">{session.tool_call_count}</p>
                </div>
                <div>
                  <p className="text-xs text-zinc-500">Tokens</p>
                  <p className="text-sm font-medium text-zinc-100 mt-0.5">
                    {formatTokens(session.total_tokens)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-zinc-500">Started</p>
                  <p className="text-sm font-medium text-zinc-100 mt-0.5">
                    {formatDateTime(session.started_at)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 lg:grid-cols-3">
            {/* Messages timeline */}
            <div className="lg:col-span-2 space-y-3">
              <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Messages</h2>
              <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
                {session.messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`rounded-lg border p-3 ${
                      msg.role === "user"
                        ? "border-zinc-700 bg-zinc-800/40"
                        : "border-blue-900/40 bg-blue-950/20"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      {msg.role === "user" ? (
                        <User className="h-3.5 w-3.5 text-zinc-400" />
                      ) : (
                        <Cpu className="h-3.5 w-3.5 text-blue-400" />
                      )}
                      <span className="text-xs font-medium text-zinc-400 capitalize">{msg.role}</span>
                      {msg.timestamp && (
                        <span className="text-xs text-zinc-600 ml-auto">
                          {formatDateTime(msg.timestamp)}
                        </span>
                      )}
                    </div>
                    {msg.content_summary && (
                      <p className="text-sm text-zinc-300 leading-relaxed">{msg.content_summary}</p>
                    )}
                    {(msg.input_tokens > 0 || msg.output_tokens > 0) && (
                      <div className="mt-1.5 flex gap-3 text-[10px] text-zinc-600">
                        {msg.input_tokens > 0 && <span>↑ {msg.input_tokens.toLocaleString()}</span>}
                        {msg.output_tokens > 0 && <span>↓ {msg.output_tokens.toLocaleString()}</span>}
                        {msg.cache_read_tokens > 0 && (
                          <span className="text-emerald-700">⚡ {msg.cache_read_tokens.toLocaleString()}</span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Tool usage sidebar */}
            <div className="space-y-3">
              <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Tool Usage</h2>
              {session.tool_usages.length === 0 ? (
                <p className="text-sm text-zinc-600">No tools used</p>
              ) : (
                <div className="space-y-2">
                  {session.tool_usages
                    .sort((a, b) => b.execution_count - a.execution_count)
                    .map((t) => (
                      <div key={t.tool_name} className="flex items-center justify-between rounded-md border border-zinc-800 px-3 py-2">
                        <span className="text-sm text-zinc-300 font-mono">{t.tool_name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-zinc-400">{t.execution_count}</span>
                          {t.is_error_count > 0 && (
                            <Badge variant="red">{t.is_error_count} err</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>
        </>
      ) : (
        <p className="text-zinc-600">Session not found.</p>
      )}
    </div>
  );
}
