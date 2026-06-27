"use client";
import { useRef, useState } from "react";
import { uploadContract, listContracts } from "@/lib/api";
import { useStore } from "@/store";

export function ContractUploader({ onUploaded }: { onUploaded?: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState<string>("");
  const setContract = useStore((s) => s.setContract);
  const resetAnalysis = useStore((s) => s.resetAnalysis);

  async function handleFile(file: File) {
    setBusy(true);
    setError(null);
    setStage(`Parsing ${file.name}…`);
    try {
      setStage("Extracting clauses & mapping to GDPR…");
      const result = await uploadContract(file, {
        title: file.name.replace(/\.[^.]+$/, ""),
      });
      setStage("Loading contract…");
      await listContracts();
      setContract(result.contract_id);
      resetAnalysis();
      onUploaded?.();
      setStage("");
    } catch (e) {
      setError(String(e instanceof Error ? e.message : e));
      setStage("");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="space-y-2">
      <div className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold px-1">
        Upload Contract
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt,.md"
        className="hidden"
        disabled={busy}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleFile(f);
        }}
      />
      <button
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        className="w-full px-3 py-2.5 rounded-lg text-[12px] font-medium bg-accent/15 border border-accent/40 text-white hover:bg-accent/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {busy ? stage || "Uploading…" : "+ Upload PDF / DOCX / TXT"}
      </button>
      <div className="text-[10px] text-slate-500 px-1 leading-relaxed">
        Auto-segments clauses · Maps to GDPR · Runs Ghost Node analysis
      </div>
      {error && (
        <div className="text-[10px] text-red-400 break-words px-1 mt-1">
          {error}
        </div>
      )}
    </div>
  );
}
