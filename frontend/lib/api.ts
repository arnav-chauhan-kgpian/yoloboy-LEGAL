import type { ContractSummary, GraphPayload } from "@/types";

const BASE = "/api";

export async function listContracts(): Promise<ContractSummary[]> {
  const res = await fetch(`${BASE}/contracts`);
  if (!res.ok) throw new Error("Failed to list contracts");
  return res.json();
}

export async function getGraph(
  contractId: string,
  includeGaps = false,
): Promise<GraphPayload> {
  const url = new URL(`${BASE}/graph/${contractId}`, window.location.origin);
  if (includeGaps) url.searchParams.set("include_gaps", "true");
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch graph");
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export function analyzeStreamUrl() {
  return `${BASE}/analyze`;
}
