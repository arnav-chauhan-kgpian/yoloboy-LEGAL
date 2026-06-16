"use client";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";

type Data = { label: string; data: Record<string, unknown>; is_gap?: boolean };
type LexNode = Node<Data>;

export function ContractNode({ data }: NodeProps<LexNode>) {
  return (
    <div className="rounded-xl shadow-md border border-slate-700 min-w-[170px]"
         style={{ background: "linear-gradient(135deg, #1E2030 0%, #161824 100%)" }}>
      <div className="px-4 py-3">
        <div className="text-[9px] font-bold uppercase tracking-widest text-slate-500 mb-1">Contract</div>
        <div className="text-[13px] font-semibold text-white leading-snug">{data.label}</div>
      </div>
      <Handle type="source" position={Position.Right}
              style={{ background: "#6366F1", border: "2px solid #818CF8", width: 8, height: 8 }} />
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
      <Handle type="target" position={Position.Left}
              style={{ background: "#F59E0B", border: "2px solid #FCD34D", width: 7, height: 7 }} />
      <Handle type="source" position={Position.Right}
              style={{ background: "#F59E0B", border: "2px solid #FCD34D", width: 7, height: 7 }} />
    </div>
  );
}

export function RequirementNode({ data }: NodeProps<LexNode>) {
  if (data.is_gap) {
    return (
      <div className="rounded-xl min-w-[170px] overflow-hidden"
           style={{
             border: "2px dashed #E11D48",
             background: "rgba(225, 29, 72, 0.06)",
             boxShadow: "0 0 12px 3px rgba(225, 29, 72, 0.18)",
           }}>
        <div className="px-3 py-2.5">
          <div className="flex items-center gap-1.5 mb-1">
            <span style={{
              fontSize: "9px", fontWeight: 800, letterSpacing: "0.1em",
              background: "#E11D48", color: "#fff", borderRadius: "4px",
              padding: "1px 5px", display: "inline-block",
            }}>GAP</span>
            <span style={{ fontSize: "9px", color: "#E11D48", opacity: 0.8,
              textTransform: "uppercase", letterSpacing: "0.06em" }}>
              Required by law
            </span>
          </div>
          <div style={{ fontSize: "12px", fontWeight: 600, color: "#E11D48", lineHeight: 1.3 }}>
            {data.label}
          </div>
        </div>
        <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      </div>
    );
  }
  return (
    <div className="rounded-xl shadow-sm border border-indigo-200 bg-white min-w-[160px] overflow-hidden">
      <div className="h-[3px] bg-gradient-to-r from-indigo-500 to-violet-400" />
      <div className="px-3 py-2.5">
        <div className="text-[9px] font-bold uppercase tracking-widest text-indigo-500 mb-0.5">Requirement</div>
        <div className="text-[12px] font-semibold text-slate-800 leading-snug">{data.label}</div>
      </div>
      <Handle type="target" position={Position.Left}
              style={{ background: "#6366F1", border: "2px solid #A5B4FC", width: 7, height: 7 }} />
      <Handle type="source" position={Position.Right}
              style={{ background: "#6366F1", border: "2px solid #A5B4FC", width: 7, height: 7 }} />
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
      <Handle type="target" position={Position.Left}
              style={{ background: "#14B8A6", border: "2px solid #5EEAD4", width: 7, height: 7 }} />
    </div>
  );
}

export const nodeTypes = {
  Contract: ContractNode,
  Clause: ClauseNode,
  Requirement: RequirementNode,
  Case: CaseNode,
};
