import React, { createContext, useContext, useMemo, useState, useEffect } from "react";
import { addUserDrug, clearUserDrugs, getUserDrugs, UserDrug } from "../services/chatApi";
import { useProfile } from "./ProfileContext"; // ProfileContext에서 user_id 가져오기

export type Pill = {
  id: string; // 로컬에선 string으로 관리 (서버 ID는 number지만 변환)
  name: string;
  addedAt: number;
  description?: string;
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
  const { profile } = useProfile(); // user_id 가져오기
  const userId = profile.user_id || "user_12345"; // fallback

  // Load drugs from DB on mount
  useEffect(() => {
    loadPills();
  }, [userId]);

  const loadPills = async () => {
    if (!userId) return;
    const dbDrugs = await getUserDrugs(userId);
    const mapped: Pill[] = dbDrugs.map((d) => ({
      id: String(d.id),
      name: d.drug_name,
      description: d.source_mode === "manual" ? "수동 등록" : (d.item_seq ? "식별된 약물" : ""),
      addedAt: d.reg_date ? new Date(d.reg_date).getTime() : Date.now(),
    }));
    setPills(mapped);
  };

  const addPill = async (pill: { id: string; name: string; description?: string }) => {
    // Optimistic Update (UI 먼저 반영)
    const tempId = pill.id; // YOLO 등에서 온 임시 ID

    // Check duplicate (name based)
    if (pills.some(p => p.name === pill.name)) return;

    const newPill: Pill = {
      id: tempId,
      name: pill.name,
      description: pill.description,
      addedAt: Date.now()
    };

    setPills((prev) => [newPill, ...prev]);

    // Sync to DB
    try {
      const dbId = await addUserDrug(userId, pill.name, pill.description);
      if (dbId) {
        // DB ID로 교체 (나중에 삭제 등을 위해)
        setPills((prev) => prev.map(p => p.id === tempId ? { ...p, id: String(dbId) } : p));
      }
    } catch (e) {
      console.error("Failed to add pill to DB", e);
    }
  };

  const removePill = async (id: string) => {
    try {
      // Call backend API to delete from database
      const response = await fetch(`${"http://127.0.0.1:8000"}/user/drug/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        console.error("Failed to delete pill from database");
      }

      // Remove from local state
      setPills((prev) => prev.filter((p) => p.id !== id));
    } catch (error) {
      console.error("Error deleting pill:", error);
      setPills((prev) => prev.filter((p) => p.id !== id));
    }
  };

  const clearPills = async () => {
    // Optimistic Update
    setPills([]);
    await clearUserDrugs(userId);
  };

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
