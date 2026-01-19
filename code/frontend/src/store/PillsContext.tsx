import React, { createContext, useContext, useMemo, useState } from "react";

export type Pill = {
  id: string;
  name: string;
  addedAt: number;
  description?: string; // 효능, 치료제 분류 등
};

type PillsContextValue = {
  pills: Pill[];
  addPill: (pill: { id: string; name: string; description?: string }) => void;
  removePill: (id: string) => void;
  clearPills: () => void;
};

const PillsContext = createContext<PillsContextValue | null>(null);

export function PillsProvider({ children }: { children: React.ReactNode }) {
  const [pills, setPills] = useState<Pill[]>([]);

  const addPill = (pill: { id: string; name: string; description?: string }) => {
    setPills((prev) => {
      // 중복 방지(이미 있으면 추가 안 함)
      if (prev.some((p) => p.id === pill.id)) return prev;

      return [{
        id: pill.id,
        name: pill.name,
        description: pill.description,
        addedAt: Date.now()
      }, ...prev];
    });
  };

  const removePill = async (id: string) => {
    try {
      // Call backend API to delete from database
      const response = await fetch(`http://127.0.0.1:8000/user/drug/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        console.error("Failed to delete pill from database");
        // Still remove from local state even if API fails
      }

      // Remove from local state
      setPills((prev) => prev.filter((p) => p.id !== id));
    } catch (error) {
      console.error("Error deleting pill:", error);
      // Still remove from local state even if API fails
      setPills((prev) => prev.filter((p) => p.id !== id));
    }
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
