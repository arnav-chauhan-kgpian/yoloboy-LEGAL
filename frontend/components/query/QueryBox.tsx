"use client";
import { useState } from "react";
import { useStore } from "@/store";
import { useAnalysis } from "@/hooks/useAnalysis";

const SUGGESTIONS = [
  "Which clauses in this contract create compliance risk under GDPR?",
  "What GDPR obligations does this contract fail to address entirely?",
  "Show me the enforcement cases behind the 72-hour breach notification requirement.",
];

export function QueryBox() {
  const [q, setQ] = useState(SUGGESTIONS[1]);
  const { run } = useAnalysis();
  const contractId = useStore((s) => s.contractId);
  const streaming = useStore((s) => s.streaming);

  const submit = () => {
    if (!contractId || !q.trim() || streaming) return;
    run(contractId, q.trim());
  };

  return (
    <div className="space-y-3">
      <div className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold px-1">
        Query
      </div>

      <textarea
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submit(); }}
        rows={4}
        placeholder="Ask LexGraph about this contract…"
        className="w-full bg-white/[0.05] border border-white/[0.10] rounded-lg px-3 py-2.5 text-[12px] text-white placeholder:text-slate-600 resize-none focus:outline-none focus:border-accent/60 focus:bg-white/[0.07] transition-all leading-relaxed"
      />

      <div className="flex gap-1.5">
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            onClick={() => setQ(s)}
            title={s}
            className="text-[10px] px-2.5 py-1 border border-white/[0.10] rounded-md text-slate-500 hover:text-slate-300 hover:border-white/20 transition-all bg-white/[0.03]"
          >
            Q{i + 1}
          </button>
        ))}
      </div>

      <button
        onClick={submit}
        disabled={!contractId || streaming}
        className="w-full py-2.5 rounded-lg text-[13px] font-semibold transition-all disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        style={{ background: streaming ? "#4338CA" : "#6366F1" }}
      >
        {streaming ? (
          <>
            <span className="w-3 h-3 rounded-full border-2 border-white/30 border-t-white animate-spin" />
            Analyzing…
          </>
        ) : (
          <>
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M6.5 1.5L11 6.5L6.5 11.5" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 6.5H11" stroke="white" strokeWidth="1.6" strokeLinecap="round"/>
            </svg>
            Analyze
          </>
        )}
      </button>
    </div>
  );
}
