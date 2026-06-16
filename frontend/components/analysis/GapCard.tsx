import type { Gap } from "@/types";

export function GapCard({ gap }: { gap: Gap }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      <div className="h-[3px] bg-gradient-to-r from-gap to-rose-400" />
      <div className="p-4">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span className="text-[10px] font-bold uppercase tracking-widest bg-gap/10 text-gap px-2 py-0.5 rounded-full">
            {gap.severity}
          </span>
          <span className="text-[13px] font-semibold text-slate-900">{gap.article}</span>
          <span className="text-[12px] text-slate-500">— {gap.title}</span>
        </div>
        <p className="text-[12px] text-slate-600 leading-relaxed">{gap.rationale}</p>
        {gap.citation_anchors.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-100 text-[10px] text-slate-400 font-mono">
            {gap.citation_anchors.join(" · ")}
          </div>
        )}
      </div>
    </div>
  );
}
