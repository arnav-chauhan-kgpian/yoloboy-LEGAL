"use client";
import { useState } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";

type CaseInfo = {
  case_id?: string;
  case_name?: string;
  authority?: string;
  year?: number;
  penalty_eur?: number | null;
  holding?: string;
};

type Data = {
  label: string;
  data: Record<string, unknown> & { cases?: CaseInfo[]; title?: string; verbatim_text?: string };
  is_gap?: boolean;
};
type LexNode = Node<Data>;

function fmtEUR(eur: number | null | undefined): string {
  if (eur == null) return "—";
  if (eur >= 1_000_000_000) return `€${(eur / 1_000_000_000).toFixed(1)}B`;
  if (eur >= 1_000_000) return `€${(eur / 1_000_000).toFixed(0)}M`;
  if (eur >= 1_000) return `€${(eur / 1_000).toFixed(0)}K`;
  return `€${eur}`;
}

function RequirementTooltip({ data, isGap }: { data: Data["data"]; isGap: boolean }) {
  const cases = data.cases ?? [];
  return (
    <div
      className="nodrag nopan"
      style={{
        position: "absolute",
        top: "calc(100% + 8px)",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 50,
        minWidth: 280,
        maxWidth: 340,
        background: "#0F1220",
        border: `1px solid ${isGap ? "#E11D48" : "#6366F1"}`,
        borderRadius: 10,
        boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
        padding: "10px 12px",
        color: "#E5E7EB",
        fontFamily: "Inter, system-ui, sans-serif",
        pointerEvents: "none",
      }}
    >
      {data.title && (
        <div style={{ fontSize: 12, fontWeight: 600, color: "#F9FAFB", marginBottom: 4 }}>
          {String(data.title)}
        </div>
      )}
      {data.verbatim_text && (
        <div style={{ fontSize: 10.5, color: "#9CA3AF", lineHeight: 1.45, marginBottom: 8 }}>
          {String(data.verbatim_text).slice(0, 180)}
          {String(data.verbatim_text).length > 180 ? "…" : ""}
        </div>
      )}
      {cases.length > 0 ? (
        <>
          <div
            style={{
              fontSize: 9,
              fontWeight: 700,
              color: isGap ? "#FCA5A5" : "#A5B4FC",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              marginBottom: 6,
              borderTop: "1px solid #1F2333",
              paddingTop: 6,
            }}
          >
            Enforcement precedent
          </div>
          {cases.slice(0, 2).map((c, i) => (
            <div key={c.case_id ?? i} style={{ marginBottom: i < cases.length - 1 ? 6 : 0 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 600, color: "#F3F4F6" }}>
                  {c.case_name ?? "Unknown case"}
                </span>
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: "#E11D48",
                    fontFamily: "ui-monospace, monospace",
                  }}
                >
                  {fmtEUR(c.penalty_eur)}
                </span>
              </div>
              <div style={{ fontSize: 10, color: "#6B7280", marginTop: 1 }}>
                {c.authority}
                {c.year ? ` · ${c.year}` : ""}
              </div>
            </div>
          ))}
        </>
      ) : (
        <div style={{ fontSize: 10, color: "#6B7280", fontStyle: "italic" }}>
          No enforcement case attached yet.
        </div>
      )}
    </div>
  );
}

export function ContractNode({ data }: NodeProps<LexNode>) {
  return (
    <div
      className="rounded-xl shadow-md border border-slate-700 min-w-[170px]"
      style={{ background: "linear-gradient(135deg, #1E2030 0%, #161824 100%)" }}
    >
      <div className="px-4 py-3">
        <div className="text-[9px] font-bold uppercase tracking-widest text-slate-500 mb-1">Contract</div>
        <div className="text-[13px] font-semibold text-white leading-snug">{data.label}</div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: "#6366F1", border: "2px solid #818CF8", width: 8, height: 8 }}
      />
    </div>
  );
}

export function ClauseNode({ data }: NodeProps<LexNode>) {
  return (
    <div className="rounded-xl shadow-sm border border-amber-200 bg-white min-w-[160px] overflow-hidden">
      <div className="h-[3px] bg-gradient-to-r from-amber-400 to-orange-300" />
      <div className="px-3 py-2.5">
        <div className="text-[9px] font-bold uppercase tracking-widest text-amber-600 mb-0.5">Clause</div>
        <div className="text-[12px] font-semibold text-slate-800 leading-snug">{data.label}</div>
      </div>
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: "#F59E0B", border: "2px solid #FCD34D", width: 7, height: 7 }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: "#F59E0B", border: "2px solid #FCD34D", width: 7, height: 7 }}
      />
    </div>
  );
}

export function RequirementNode({ data }: NodeProps<LexNode>) {
  const [hover, setHover] = useState(false);
  const isGap = !!data.is_gap;

  const inner = isGap ? (
    <div
      className="rounded-xl min-w-[170px] overflow-hidden"
      style={{
        border: "2px dashed #E11D48",
        background: "rgba(225, 29, 72, 0.06)",
        boxShadow: hover ? "0 0 18px 5px rgba(225, 29, 72, 0.4)" : "0 0 12px 3px rgba(225, 29, 72, 0.18)",
        transition: "box-shadow 0.15s ease",
        cursor: "help",
      }}
    >
      <div className="px-3 py-2.5">
        <div className="flex items-center gap-1.5 mb-1">
          <span
            style={{
              fontSize: "9px",
              fontWeight: 800,
              letterSpacing: "0.1em",
              background: "#E11D48",
              color: "#fff",
              borderRadius: "4px",
              padding: "1px 5px",
              display: "inline-block",
            }}
          >
            GAP
          </span>
          <span
            style={{
              fontSize: "9px",
              color: "#E11D48",
              opacity: 0.8,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
            }}
          >
            Required by law
          </span>
        </div>
        <div style={{ fontSize: "12px", fontWeight: 600, color: "#E11D48", lineHeight: 1.3 }}>
          {data.label}
        </div>
      </div>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
    </div>
  ) : (
    <div
      className="rounded-xl shadow-sm border border-indigo-200 bg-white min-w-[160px] overflow-hidden"
      style={{ cursor: "help" }}
    >
      <div className="h-[3px] bg-gradient-to-r from-indigo-500 to-violet-400" />
      <div className="px-3 py-2.5">
        <div className="text-[9px] font-bold uppercase tracking-widest text-indigo-500 mb-0.5">Requirement</div>
        <div className="text-[12px] font-semibold text-slate-800 leading-snug">{data.label}</div>
      </div>
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: "#6366F1", border: "2px solid #A5B4FC", width: 7, height: 7 }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: "#6366F1", border: "2px solid #A5B4FC", width: 7, height: 7 }}
      />
    </div>
  );

  return (
    <div
      style={{ position: "relative" }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      {inner}
      {hover && <RequirementTooltip data={data.data} isGap={isGap} />}
    </div>
  );
}

export function CaseNode({ data }: NodeProps<LexNode>) {
  return (
    <div className="rounded-xl shadow-sm border border-teal-200 bg-white min-w-[160px] overflow-hidden">
      <div className="h-[3px] bg-gradient-to-r from-teal-500 to-emerald-400" />
      <div className="px-3 py-2.5">
        <div className="text-[9px] font-bold uppercase tracking-widest text-teal-600 mb-0.5">Case</div>
        <div className="text-[12px] font-semibold text-slate-800 leading-snug">{data.label}</div>
      </div>
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: "#14B8A6", border: "2px solid #5EEAD4", width: 7, height: 7 }}
      />
    </div>
  );
}

export const nodeTypes = {
  Contract: ContractNode,
  Clause: ClauseNode,
  Requirement: RequirementNode,
  Case: CaseNode,
};
