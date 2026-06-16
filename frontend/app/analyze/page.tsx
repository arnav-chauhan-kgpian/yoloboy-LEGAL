"use client";
import { useStore } from "@/store";
import { useGraph } from "@/hooks/useGraph";
import { AppShell } from "@/components/layout/AppShell";
import { ContractSelector } from "@/components/contract/ContractSelector";
import { QueryBox } from "@/components/query/QueryBox";
import { LegalGraph } from "@/components/graph/LegalGraph";
import { ReportPanel } from "@/components/analysis/ReportPanel";

export default function AnalyzePage() {
  const contractId = useStore((s) => s.contractId);
  useGraph(contractId, false);

  return (
    <AppShell
      sidebar={
        <div className="space-y-4">
          <ContractSelector />
          <QueryBox />
        </div>
      }
      graph={<LegalGraph />}
      panel={<ReportPanel />}
    />
  );
}
