"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useCallback, Suspense } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { api } from "@/lib/api";
import { SyncButton } from "@/components/layout/sync-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  formatTokens,
  formatCost,
  formatDateTime,
  formatDuration,
  modelDisplayName,
  truncateSessionId,
} from "@/lib/utils";

function SessionsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project_id");

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
    const timeout = setTimeout(() => {
      setDebouncedSearch(value);
      setPage(1);
    }, 300);
    return () => clearTimeout(timeout);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["sessions", { page, search: debouncedSearch, projectId }],
    queryFn: () =>
      api
        .sessions({
          page,
          page_size: 20,
          search: debouncedSearch || undefined,
          project_id: projectId ? parseInt(projectId) : undefined,
        })
        .then((r) => r.data),
    placeholderData: (prev) => prev,
  });

  const sessions = data?.items ?? [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">Sessions</h1>
        <SyncButton />
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
          <Input
            placeholder="Search sessions or projects…"
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        {projectId && (
          <Button variant="ghost" size="sm" onClick={() => router.push("/sessions")}>
            Clear filter
          </Button>
        )}
      </div>

      <div className="rounded-lg border border-zinc-800 overflow-hidden">
        <table className="w-full text-left">
          <thead className="border-b border-zinc-800 bg-zinc-900/50">
            <tr>
              {["Session", "Project", "Model", "Started", "Duration", "Messages", "Tokens", "Cost"].map((h) => (
                <th key={h} className="px-4 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {isLoading
              ? Array.from({ length: 10 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 8 }).map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <Skeleton className="h-4 w-16" />
                      </td>
                    ))}
                  </tr>
                ))
              : sessions.map((s) => (
                  <tr
                    key={s.id}
                    className="hover:bg-zinc-800/30 cursor-pointer transition-colors"
                    onClick={() => router.push(`/sessions/${s.id}`)}
                  >
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs text-zinc-400">
                        {truncateSessionId(s.session_id)}
                        {s.has_compaction && (
                          <span className="ml-1 text-[10px] text-amber-500" title="Context was compacted">
                            ~
                          </span>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-300">{s.project_name}</span>
                    </td>
                    <td className="px-4 py-3">
                      {s.model ? (
                        <Badge variant="blue">{modelDisplayName(s.model)}</Badge>
                      ) : (
                        <span className="text-zinc-600">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-400">{formatDateTime(s.started_at)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-400">{formatDuration(s.duration_minutes)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-300">{s.message_count.toLocaleString()}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-300">{formatTokens(s.total_tokens)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-zinc-300">{formatCost(s.estimated_cost)}</span>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
        {!isLoading && sessions.length === 0 && (
          <div className="py-16 text-center text-sm text-zinc-600">No sessions found.</div>
        )}
      </div>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-between text-sm text-zinc-400">
          <span>
            {((page - 1) * 20 + 1).toLocaleString()}–{Math.min(page * 20, data.total).toLocaleString()} of{" "}
            {data.total.toLocaleString()} sessions
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="px-3 py-1 text-xs">
              {page} / {data.pages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= data.pages}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SessionsPage() {
  return (
    <Suspense>
      <SessionsContent />
    </Suspense>
  );
}
