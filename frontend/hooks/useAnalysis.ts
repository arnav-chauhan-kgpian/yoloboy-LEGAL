"use client";
import { useCallback } from "react";
import { useStore } from "@/store";
import { analyzeStreamUrl } from "@/lib/api";
import type { AgentResult, Citation, Gap, GraphPayload, Risk } from "@/types";

export function useAnalysis() {
  const store = useStore();

  const run = useCallback(
    async (contractId: string, query: string, frameworkId = "gdpr_2016_679") => {
      store.resetAnalysis();
      store.setStreaming(true);

      try {
        const res = await fetch(analyzeStreamUrl(), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ contract_id: contractId, query, framework_id: frameworkId }),
        });

        if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const blocks = buffer.split("\n\n");
          buffer = blocks.pop() ?? "";

          for (const block of blocks) {
            const lines = block.split("\n");
            let event = "message";
            let dataStr = "";
            for (const line of lines) {
              if (line.startsWith("event:")) event = line.slice(6).trim();
              else if (line.startsWith("data:")) dataStr += line.slice(5).trim();
            }
            if (!dataStr) continue;
            let data: unknown;
            try { data = JSON.parse(dataStr); } catch { continue; }

            switch (event) {
              case "stage":
                store.pushStage(data as { stage: string; message: string });
                break;
              case "graph_data":
                store.setGraph(data as GraphPayload);
                break;
              case "gaps":
                store.setGaps((data as { gaps: Gap[] }).gaps);
                break;
              case "risks":
                store.setRisks((data as { risks: Risk[] }).risks);
                break;
              case "citations":
                store.setCitations((data as { citations: Citation[] }).citations);
                break;
              case "synthesis_chunk":
                store.appendSummary((data as { text: string }).text);
                break;
              case "complete":
                store.setResult(data as AgentResult);
                break;
              case "error":
                store.setError((data as { message: string }).message);
                break;
            }
          }
        }
      } catch (e) {
        store.setError(e instanceof Error ? e.message : String(e));
      } finally {
        store.setStreaming(false);
      }
    },
    [store],
  );

  return { run };
}
