"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  flexRender,
} from "@tanstack/react-table";
import { useState, useMemo } from "react";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { api } from "@/lib/api";
import { SyncButton } from "@/components/layout/sync-button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatTokens, formatCost, formatDate, modelDisplayName } from "@/lib/utils";
import type { ProjectSummary } from "@/types/api";

export default function RepositoriesPage() {
  const router = useRouter();
  const [sorting, setSorting] = useState<SortingState>([{ id: "total_sessions", desc: true }]);

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => api.projects().then((r) => r.data),
  });

  const columns = useMemo(
    () => [
      {
        accessorKey: "name",
        header: "Repository",
        cell: ({ row }: { row: { original: ProjectSummary } }) => (
          <div>
            <p className="text-sm font-medium text-zinc-100">{row.original.name}</p>
            <p className="text-xs text-zinc-600 font-mono">{row.original.path || row.original.slug}</p>
          </div>
        ),
      },
      {
        accessorKey: "total_sessions",
        header: "Sessions",
        cell: ({ getValue }: { getValue: () => number }) => (
          <span className="text-sm text-zinc-300">{getValue().toLocaleString()}</span>
        ),
      },
      {
        accessorKey: "sessions_30d",
        header: "30d Sessions",
        cell: ({ getValue }: { getValue: () => number }) => (
          <span className="text-sm text-zinc-300">{getValue().toLocaleString()}</span>
        ),
      },
      {
        accessorKey: "total_tokens",
        header: "Total Tokens",
        cell: ({ getValue }: { getValue: () => number }) => (
          <span className="text-sm text-zinc-300">{formatTokens(getValue())}</span>
        ),
      },
      {
        accessorKey: "estimated_cost",
        header: "Est. Cost",
        cell: ({ getValue }: { getValue: () => number }) => (
          <span className="text-sm text-zinc-300">{formatCost(getValue())}</span>
        ),
      },
      {
        accessorKey: "most_used_model",
        header: "Model",
        cell: ({ getValue }: { getValue: () => string | null }) => {
          const m = getValue();
          return m ? <Badge variant="blue">{modelDisplayName(m)}</Badge> : <span className="text-zinc-600">—</span>;
        },
      },
      {
        accessorKey: "last_active",
        header: "Last Active",
        cell: ({ getValue }: { getValue: () => string | null }) => (
          <span className="text-sm text-zinc-400">{formatDate(getValue())}</span>
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data: projects,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">Repositories</h1>
        <SyncButton />
      </div>

      <div className="rounded-lg border border-zinc-800 overflow-hidden">
        <table className="w-full text-left">
          <thead className="border-b border-zinc-800 bg-zinc-900/50">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider cursor-pointer hover:text-zinc-300 select-none"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? (
                        <ArrowUp className="h-3 w-3" />
                      ) : header.column.getIsSorted() === "desc" ? (
                        <ArrowDown className="h-3 w-3" />
                      ) : (
                        <ArrowUpDown className="h-3 w-3 opacity-30" />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {isLoading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {columns.map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <Skeleton className="h-4 w-24" />
                      </td>
                    ))}
                  </tr>
                ))
              : table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="hover:bg-zinc-800/30 cursor-pointer transition-colors"
                    onClick={() => router.push(`/sessions?project_id=${row.original.id}`)}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-4 py-3">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
          </tbody>
        </table>
        {!isLoading && projects.length === 0 && (
          <div className="py-16 text-center text-sm text-zinc-600">
            No repositories found. Click Sync to discover projects.
          </div>
        )}
      </div>
    </div>
  );
}
