import type { ContractSummary, GraphPayload } from "@/types";

const BASE = "/api";

export async function listContracts(): Promise<ContractSummary[]> {
  const res = await fetch(`${BASE}/contracts`);
  if (!res.ok) throw new Error(`Failed to list contracts: ${res.status} ${res.statusText}`);
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

export async function uploadContract(
  file: File,
  opts: { title?: string; parties?: string; governing_law?: string } = {},
): Promise<{ contract_id: string; clause_count: number }> {
  const form = new FormData();
  form.append("file", file);
  if (opts.title) form.append("title", opts.title);
  if (opts.parties) form.append("parties", opts.parties);
  if (opts.governing_law) form.append("governing_law", opts.governing_law);
  const res = await fetch(`${BASE}/contracts/upload`, { method: "POST", body: form });
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try {
      const data = await res.json();
      msg = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}
