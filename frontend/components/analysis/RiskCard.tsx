import type { Risk } from "@/types";

const sevConfig: Record<string, { bar: string; badge: string }> = {
  CRITICAL: { bar: "from-gap to-rose-400",    badge: "bg-gap/10 text-gap" },
  HIGH:     { bar: "from-warn to-amber-400",   badge: "bg-warn/10 text-warn" },
  MEDIUM:   { bar: "from-slate-400 to-slate-300", badge: "bg-slate-100 text-slate-600" },
  LOW:      { bar: "from-slate-300 to-slate-200", badge: "bg-slate-50 text-slate-500" },
};

export function RiskCard({ risk }: { risk: Risk }) {
  const cfg = sevConfig[risk.severity] ?? sevConfig.MEDIUM;
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      <div className={`h-[3px] bg-gradient-to-r ${cfg.bar}`} />
      <div className="p-4">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${cfg.badge}`}>
            {risk.severity}
          </span>
          <span className="text-[12px] font-semibold text-slate-900">{risk.clause_section}</span>
          <span className="text-[11px] text-slate-400">↔</span>
          <span className="text-[12px] text-slate-600">{risk.article}</span>
        </div>
        <p className="text-[12px] text-slate-600 leading-relaxed">{risk.rationale}</p>
        <div className="mt-2 text-[10px] font-mono uppercase tracking-wider text-slate-400">
          {risk.conflict_type}
        </div>
      </div>
    </div>
  );
}
