"use client";
import { useEffect } from "react";
import { useStore } from "@/store";
import { getGraph } from "@/lib/api";

export function useGraph(contractId: string | null, includeGaps = false) {
  const setGraph = useStore((s) => s.setGraph);

  useEffect(() => {
    if (!contractId) return;
    let cancelled = false;
    (async () => {
      try {
        const g = await getGraph(contractId, includeGaps);
        if (!cancelled) setGraph(g);
      } catch {
        if (!cancelled) setGraph(null);
      }
    })();
    return () => { cancelled = true; };
  }, [contractId, includeGaps, setGraph]);
}
