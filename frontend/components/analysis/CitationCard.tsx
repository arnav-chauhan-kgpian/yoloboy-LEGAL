import type { Citation } from "@/types";

function fmtEUR(n: number | null): string {
  if (n == null) return "—";
  if (n >= 1_000_000_000) return `€${(n / 1_000_000_000).toFixed(2)}B`;
  if (n >= 1_000_000)     return `€${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)         return `€${(n / 1_000).toFixed(0)}K`;
  return `€${n}`;
}

export function CitationCard({ c }: { c: Citation }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      <div className="h-[3px] bg-gradient-to-r from-accent to-indigo-400" />
      <div className="p-4">
        <div className="flex items-start justify-between gap-3 mb-1">
          <div className="font-semibold text-[13px] text-slate-900 leading-snug">{c.case_name}</div>
          <div className="text-[18px] font-bold text-gap font-mono flex-shrink-0 leading-tight">
            {fmtEUR(c.penalty_eur)}
          </div>
        </div>
        <div className="text-[10px] uppercase tracking-widest text-slate-400 font-medium mb-2">
          {c.authority} &middot; {c.year}
        </div>
        <p className="text-[12px] text-slate-600 leading-relaxed">{c.holding}</p>
        <div className="mt-3 flex items-center gap-2">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex-shrink-0">
            Authority
          </div>
          <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent rounded-full transition-all"
              style={{ width: `${Math.round(c.authority_score * 100)}%` }}
            />
          </div>
          <div className="text-[11px] font-mono text-slate-500 flex-shrink-0">
            {c.authority_score.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
}
