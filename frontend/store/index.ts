import { create } from "zustand";
import type { AgentResult, Gap, Risk, Citation, GraphPayload, StageEvent } from "@/types";

interface State {
  contractId: string | null;
  graph: GraphPayload | null;
  stages: StageEvent[];
  gaps: Gap[];
  risks: Risk[];
  citations: Citation[];
  summary: string;
  result: AgentResult | null;
  streaming: boolean;
  error: string | null;

  setContract(id: string): void;
  setGraph(g: GraphPayload | null): void;
  pushStage(s: StageEvent): void;
  setGaps(g: Gap[]): void;
  setRisks(r: Risk[]): void;
  setCitations(c: Citation[]): void;
  appendSummary(t: string): void;
  setResult(r: AgentResult): void;
  setStreaming(s: boolean): void;
  setError(e: string | null): void;
  resetAnalysis(): void;
}

export const useStore = create<State>((set) => ({
  contractId: null,
  graph: null,
  stages: [],
  gaps: [],
  risks: [],
  citations: [],
  summary: "",
  result: null,
  streaming: false,
  error: null,

  setContract: (id) => set({ contractId: id }),
  setGraph: (g) => set({ graph: g }),
  pushStage: (s) => set((st) => ({ stages: [...st.stages, s] })),
  setGaps: (g) => set({ gaps: g }),
  setRisks: (r) => set({ risks: r }),
  setCitations: (c) => set({ citations: c }),
  appendSummary: (t) => set((st) => ({ summary: st.summary + t })),
  setResult: (r) => set({ result: r }),
  setStreaming: (s) => set({ streaming: s }),
  setError: (e) => set({ error: e }),
  resetAnalysis: () =>
    set({
      stages: [],
      gaps: [],
      risks: [],
      citations: [],
      summary: "",
      result: null,
      error: null,
    }),
}));
