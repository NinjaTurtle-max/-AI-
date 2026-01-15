import React, { createContext, useContext, useMemo, useState } from "react";

export type Pill = {
  id: string;
  name: string;
  addedAt: number;
};

type PillsContextValue = {
  pills: Pill[];
  addPill: (pill: { id: string; name: string }) => void;
  removePill: (id: string) => void;
  clearPills: () => void;
};

const PillsContext = createContext<PillsContextValue | null>(null);

export function PillsProvider({ children }: { children: React.ReactNode }) {
  const [pills, setPills] = useState<Pill[]>([]);

  const addPill = (pill: { id: string; name: string }) => {
    setPills((prev) => {
      // 중복 방지(이미 있으면 추가 안 함)
      if (prev.some((p) => p.id === pill.id)) return prev;

      return [{ id: pill.id, name: pill.name, addedAt: Date.now() }, ...prev];
    });
  };

  const removePill = (id: string) => {
    setPills((prev) => prev.filter((p) => p.id !== id));
  };

  const clearPills = () => setPills([]);

  const value = useMemo(
    () => ({ pills, addPill, removePill, clearPills }),
    [pills]
  );

  return <PillsContext.Provider value={value}>{children}</PillsContext.Provider>;
}

export function usePills() {
  const ctx = useContext(PillsContext);
  if (!ctx) throw new Error("usePills must be used within PillsProvider");
  return ctx;
}
