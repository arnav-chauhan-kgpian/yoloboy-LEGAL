"use client";
import { useStore } from "@/store";
import { GapCard } from "./GapCard";
import { RiskCard } from "./RiskCard";
import { CitationCard } from "./CitationCard";
import { StreamingResponse } from "./StreamingResponse";

export function ReportPanel() {
  const { gaps, risks, citations, summary, streaming } = useStore();
  const hasContent = gaps.length > 0 || risks.length > 0 || citations.length > 0 || summary.length > 0;

  return (
    <div className="h-full flex flex-col">
      {/* Panel header */}
      <div className="px-5 py-4 border-b border-slate-100 flex-shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-[13px] font-semibold text-slate-900">Analysis</h2>
          {hasContent && (
            <div className="flex gap-3 text-[11px]">
              {gaps.length > 0 && (
                <span className="text-gap font-medium">{gaps.length} gaps</span>
              )}
              {risks.length > 0 && (
                <span className="text-warn font-medium">{risks.length} conflicts</span>
              )}
              {citations.length > 0 && (
                <span className="text-accent font-medium">{citations.length} citations</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-5">
          <StreamingResponse />

          {summary && (
            <div className="text-[13px] text-slate-700 bg-slate-50 border border-slate-200 rounded-xl p-4 leading-relaxed">
              {summary}
            </div>
          )}

          {gaps.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 rounded-full bg-gap" />
                <h3 className="text-[11px] font-bold uppercase tracking-widest text-gap">
                  Missing Requirements
                </h3>
                <span className="ml-auto text-[11px] font-medium text-slate-400">{gaps.length}</span>
              </div>
              <div className="space-y-2.5">
                {gaps.map((g) => <GapCard key={g.requirement_id} gap={g} />)}
              </div>
            </section>
          )}

          {risks.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 rounded-full bg-warn" />
                <h3 className="text-[11px] font-bold uppercase tracking-widest text-warn">
                  Conflicts
                </h3>
                <span className="ml-auto text-[11px] font-medium text-slate-400">{risks.length}</span>
              </div>
              <div className="space-y-2.5">
                {risks.map((r) => (
                  <RiskCard key={`${r.clause_id}__${r.requirement_id}`} risk={r} />
                ))}
              </div>
            </section>
          )}

          {citations.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 rounded-full bg-accent" />
                <h3 className="text-[11px] font-bold uppercase tracking-widest text-accent">
                  Cited Cases
                </h3>
                <span className="ml-auto text-[11px] font-medium text-slate-400">{citations.length}</span>
              </div>
              <div className="space-y-2.5">
                {citations.map((c) => <CitationCard key={c.case_id} c={c} />)}
              </div>
            </section>
          )}

          {!hasContent && !streaming && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center mb-3">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M9 3v6l4 2" stroke="#94A3B8" strokeWidth="1.6" strokeLinecap="round"/>
                  <circle cx="9" cy="9" r="7" stroke="#94A3B8" strokeWidth="1.4"/>
                </svg>
              </div>
              <div className="text-[13px] font-medium text-slate-400">Ready to analyze</div>
              <div className="text-[11px] text-slate-400 mt-1">Select a contract and run a query</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
