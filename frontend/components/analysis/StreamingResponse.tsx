"use client";
import { useStore } from "@/store";

export function StreamingResponse() {
  const stages = useStore((s) => s.stages);
  const streaming = useStore((s) => s.streaming);
  const error = useStore((s) => s.error);

  if (error) {
    return (
      <div className="rounded-xl border border-gap/30 bg-gap/5 p-3 text-[12px] text-gap">
        <span className="font-semibold">Error: </span>{error}
      </div>
    );
  }
  if (stages.length === 0 && !streaming) return null;

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 space-y-2">
      {stages.map((s, i) => {
        const isLast = i === stages.length - 1;
        return (
          <div key={i} className="flex items-start gap-2.5">
            <div className={`mt-[3px] w-2 h-2 rounded-full flex-shrink-0 ${
              isLast && streaming ? "bg-accent animate-pulse" : "bg-slate-300"
            }`} />
            <div>
              <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                {s.stage}
              </div>
              <div className="text-[12px] text-slate-600">{s.message}</div>
            </div>
          </div>
        );
      })}
      {streaming && stages.length === 0 && (
        <div className="flex items-center gap-2.5">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse flex-shrink-0" />
          <div className="text-[12px] text-slate-500">Starting analysis…</div>
        </div>
      )}
    </div>
  );
}
