export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface Citation {
  case_id: string;
  case_name: string;
  authority: string;
  year: number;
  penalty_eur: number | null;
  holding: string;
  authority_score: number;
}

export interface Gap {
  requirement_id: string;
  article: string;
  title: string;
  severity: Severity;
  rationale: string;
  citation_anchors: string[];
}

export interface Risk {
  clause_id: string;
  clause_section: string;
  requirement_id: string;
  article: string;
  conflict_type: string;
  severity: Severity;
  rationale: string;
  citation_anchors: string[];
}

export interface AgentResult {
  contract_id: string;
  query: string;
  gaps: Gap[];
  risks: Risk[];
  citations: Citation[];
  summary: string;
  gap_count: number;
  risk_count: number;
}

export interface GraphNode {
  id: string;
  type: "Contract" | "Clause" | "Requirement" | "Case" | "ComplianceFramework" | "Risk" | "Court" | "Report";
  label: string;
  data: Record<string, unknown>;
  is_gap: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  animated: boolean;
  data?: Record<string, unknown>;
}

export interface GraphPayload {
  nodes: GraphNode[];
  edges: GraphEdge[];
  gap_node_ids: string[];
}

export interface ContractSummary {
  contract_id: string;
  title: string;
  parties: string[];
  governing_law: string;
  clause_count: number;
}

export type StageEvent = { stage: string; message: string };
