import { create } from "zustand";

interface DevLensStore {
  lastSyncAt: Date | null;
  isSyncing: boolean;
  setLastSyncAt: (date: Date) => void;
  setIsSyncing: (v: boolean) => void;
}

export const useStore = create<DevLensStore>((set) => ({
  lastSyncAt: null,
  isSyncing: false,
  setLastSyncAt: (date) => set({ lastSyncAt: date }),
  setIsSyncing: (v) => set({ isSyncing: v }),
}));
