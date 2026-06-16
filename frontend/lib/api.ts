import type { ContractSummary, GraphPayload } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function listContracts(): Promise<ContractSummary[]> {
  const res = await fetch(`${BASE}/api/contracts`);
  if (!res.ok) throw new Error("Failed to list contracts");
  return res.json();
}

export async function getGraph(
  contractId: string,
  includeGaps = false,
): Promise<GraphPayload> {
  const url = new URL(`${BASE}/api/graph/${contractId}`);
  if (includeGaps) url.searchParams.set("include_gaps", "true");
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch graph");
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${BASE}/api/health`);
  return res.json();
}

export function analyzeStreamUrl() {
  return `${BASE}/api/analyze`;
}
