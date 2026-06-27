"use client";
import { useCallback, useEffect, useState } from "react";
import { useStore } from "@/store";
import { listContracts } from "@/lib/api";
import type { ContractSummary } from "@/types";
import { ContractUploader } from "./ContractUploader";

export function ContractSelector() {
  const [contracts, setContracts] = useState<ContractSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const contractId = useStore((s) => s.contractId);
  const setContract = useStore((s) => s.setContract);
  const resetAnalysis = useStore((s) => s.resetAnalysis);

  const refresh = useCallback(async () => {
    try {
      const cs = await listContracts();
      setContracts(cs);
      setError(null);
      if (cs.length > 0 && !contractId) setContract(cs[0].contract_id);
    } catch (e) {
      setContracts([]);
      setError(String(e instanceof Error ? e.message : e));
    } finally {
      setLoading(false);
    }
  }, [contractId, setContract]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="space-y-4">
      <ContractUploader onUploaded={refresh} />

      <div className="space-y-2">
        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold px-1">
          Contracts
        </div>
        {loading ? (
          <div className="text-[11px] text-slate-500 animate-pulse px-1">Loading…</div>
        ) : contracts.length === 0 ? (
          <div className="text-[11px] text-slate-500 space-y-1 px-1">
            <div>No contracts yet. Upload one above.</div>
            {error && <div className="text-red-400 break-all">{error}</div>}
          </div>
        ) : (
          <div className="space-y-1">
            {contracts.map((c) => (
              <button
                key={c.contract_id}
                onClick={() => { setContract(c.contract_id); resetAnalysis(); }}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-[12px] transition-all ${
                  c.contract_id === contractId
                    ? "bg-accent/15 border border-accent/40 text-white"
                    : "bg-white/[0.04] border border-white/[0.08] text-slate-300 hover:bg-white/[0.07] hover:text-white"
                }`}
              >
                <div className="font-medium truncate leading-snug">{c.title}</div>
                <div className="text-[10px] mt-0.5 opacity-60 truncate">
                  {c.parties.join(" · ")}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
