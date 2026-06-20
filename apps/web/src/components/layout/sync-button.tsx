"use client";

import { RefreshCw } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/utils";

export function SyncButton() {
  const { isSyncing, setIsSyncing, setLastSyncAt } = useStore();
  const queryClient = useQueryClient();

  const handleSync = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    try {
      await api.sync();
      setLastSyncAt(new Date());
      await queryClient.invalidateQueries();
    } catch {
      // silent — user can retry
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <Button variant="outline" size="sm" onClick={handleSync} disabled={isSyncing}>
      <RefreshCw className={cn("h-3.5 w-3.5", isSyncing && "animate-spin")} />
      {isSyncing ? "Syncing…" : "Sync"}
    </Button>
  );
}
