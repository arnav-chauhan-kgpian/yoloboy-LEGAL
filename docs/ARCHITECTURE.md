# LexGraph AI — System Architecture

> This document describes the internal architecture of LexGraph AI for technical reviewers and hackathon judges.

---

## 1. System Overview

LexGraph AI is a legal intelligence platform built around a single core insight: **legal risk lives in absence, not presence**. Traditional contract analysis tools use retrieval-augmented generation to surface what a contract *says*. LexGraph models what a contract *must say* under applicable law, and detects the gap.

The system consists of four functional layers:

```
┌─────────────────────────────────────────────────────────────┐
│  INGESTION LAYER                                            │
│  JSON contracts + GDPR framework → in-memory graph store   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  KNOWLEDGE GRAPH LAYER                                      │
│  Property graph: nodes (Contract, Clause, Requirement,      │
│  Case, Court, Framework) + typed edges                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  GRAPHRAG RETRIEVAL LAYER                                   │
│  G1 (conflicts) + G2 (gaps) + G3 (precedents) + RRF fusion │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  AGENT LAYER                                                │
│  OrchestratorAgent → AnalysisAgent (Groq tool-use) → SSE   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Knowledge Graph Design

### Node Types (7)

| Type | Description | Key Properties |
|---|---|---|
| `Contract` | A legal agreement under analysis | `contract_id`, `title`, `parties`, `governing_law` |
| `Clause` | An individual provision within a contract | `clause_id`, `section`, `text`, `order` |
| `Requirement` | A legally mandated obligation from a framework | `requirement_id`, `article`, `title`, `default_severity`, `verbatim_text` |
| `ComplianceFramework` | A regulatory body of law (GDPR) | `framework_id`, `name`, `jurisdiction`, `version` |
| `Case` | An enforcement decision | `case_id`, `name`, `authority`, `year`, `penalty_eur`, `holding`, `authority_score` |
| `Court` | The tribunal that decided a case | `court_id`, `name`, `jurisdiction`, `tier` |
| `Risk` | A specific conflict type identified in a clause | `risk_id`, `conflict_type`, `severity` |

### Relationship Types (10)

| Relationship | Source → Target | Semantics |
|---|---|---|
| `HAS_CLAUSE` | Contract → Clause | Contract contains this clause |
| `HAS_REQUIREMENT` | Framework → Requirement | Framework mandates this obligation |
| `MAPS_TO` | Clause → Requirement | Clause satisfies this obligation |
| `CONFLICTS_WITH` | Clause → Requirement | Clause conflicts with this obligation |
| `ENFORCED_BY` | Case → Requirement | Case enforced this obligation |
| `DECIDED_BY` | Case → Court | Case was decided by this court |
| `CREATES_RISK` | Clause → Risk | Clause creates this risk |
| `SUBJECT_TO` | Contract → Framework | Contract is subject to this framework |
| `CITES` | Risk → Case | Risk is supported by this precedent |
| `PART_OF` | Clause → Contract | *(inverse, for traversal)* |

### Implementation

The graph is stored as an in-memory Python property graph — a set of typed dictionaries and adjacency lists. This design was chosen for:

1. **Zero infrastructure** — no Neo4j, no Docker, no port conflicts at demo time
2. **Deterministic seeding** — graph is rebuilt from JSON on every startup, guaranteeing consistency
3. **O(1) adjacency lookups** — Python `set` operations for gap detection

The graph is seeded on API startup from `data/requirements/gdpr_requirements.json` (11 GDPR articles, 9 enforcement cases) and `data/contracts/*.json`.

---

## 3. The Ghost Node Concept

A Ghost Node is a `Requirement` node that:

1. Exists in the `ComplianceFramework` subgraph (i.e., is mandated by law)
2. Has no `MAPS_TO` edge from any `Clause` in the contract under analysis
3. Is therefore **required by law but unaddressed by the contract**

Ghost Nodes are rendered in the React Flow visualization as:
- Dashed red border (2px, `#E11D48`)
- Red glow (box-shadow: `0 0 12px 3px rgba(225, 29, 72, 0.18)`)
- "GAP" badge in filled red
- Disconnected from the contract subgraph — floating, unreachable

This visual design communicates legal absence as spatial disconnection. A ghost node is not missing from the graph. It is missing from the *contract's reach* within the graph.

---

## 4. Gap Detection Workflow (G2)

The core query is a Python set-difference operation:

```python
# Step 1: All obligations mandated by the framework
all_req_ids = set(store.framework_requirements[framework_id])

# Step 2: Obligations reachable from this contract via MAPS_TO
covered_ids = set()
for clause_id in store.contract_clauses[contract_id]:
    covered_ids |= set(store.clause_maps_to[clause_id])

# Step 3: Gap = what the law requires minus what the contract addresses
gap_ids = all_req_ids - covered_ids
```

This is equivalent to the following Cypher pattern:

```cypher
MATCH (fw:ComplianceFramework)-[:HAS_REQUIREMENT]->(req)
WITH collect(req) AS all_reqs
MATCH (c:Contract)-[:HAS_CLAUSE]->(cl)-[:MAPS_TO]->(covered)
WITH all_reqs, collect(DISTINCT covered) AS covered
RETURN [r IN all_reqs WHERE NOT r IN covered] AS gaps
```

The result feeds directly into the Analysis Agent as pre-computed ground truth. The LLM does not detect gaps — it *explains* them, cites the enforcement cases that prove they matter, and generates the rationale.

---

## 5. GraphRAG Retrieval

The system uses three complementary graph traversal queries fused with dense vector search via Reciprocal Rank Fusion (RRF).

### G1 — Risk Detection
Traverses `Contract → Clause → CONFLICTS_WITH → Requirement → Case`.
Identifies clauses that explicitly conflict with GDPR obligations, returning the enforcement precedent for each conflict.

### G2 — Gap Detection ★
Described above. The central innovation of the system.

### G3 — Precedent Chain
Given a gap requirement ID, returns all enforcement cases ordered by `authority_score`.
The authority score is a normalized float encoding regulatory weight (DPA tier, penalty magnitude, recency).

### RRF Fusion
Graph results (G1/G3 context units) are fused with vector search results using Reciprocal Rank Fusion:

```
score(d) = Σ  graph_weight / (k + rank_graph(d))
         + (1 - graph_weight) / (k + rank_vector(d))
```

Parameters: `k=60`, `graph_weight=0.70`. Graph results are weighted higher because the knowledge graph encodes ground-truth legal relationships that dense retrieval cannot infer.

### Vector Search
Clauses are embedded using `sentence-transformers/all-MiniLM-L6-v2` (384-dim, local, free). Embeddings are stored in ChromaDB EphemeralClient with cosine similarity. The vector search provides semantic coverage for queries that use non-standard legal language.

---

## 6. Agents

### OrchestratorAgent

The orchestrator drives the analysis pipeline and emits Server-Sent Events at each stage:

```
stage: routing
stage: retrieving  →  fetch bundle (G1 + G2 + G3 + vector)
                   →  fetch graph payload (for React Flow)
                   →  emit: graph_data
stage: analyzing   →  call AnalysisAgent
                   →  emit: gaps, risks, citations, synthesis_chunk
                   →  emit: complete
```

### AnalysisAgent

The analysis agent uses Groq's `llama-3.3-70b-versatile` with OpenAI-compatible tool use. A single `emit_analysis` tool enforces structured output — the model must call this tool with a JSON object containing `gaps`, `risks`, `citations`, and `summary`.

**Deterministic fallback**: If the LLM call fails (network error, API timeout, malformed tool call), the agent synthesizes the result directly from the pre-computed retrieval bundle. The demo never silently empties.

The system prompt enforces citation grounding: every gap and risk must reference a `[CTX_*]` anchor from the context window, and every anchor corresponds to a real enforcement case in the knowledge graph.

---

## 7. Regulatory Reasoning

The system performs reasoning at three levels:

**Structural** — G2 gap detection identifies absence with mathematical precision. A gap exists if and only if the set-difference is non-empty. This is not probabilistic.

**Semantic** — Vector search extends coverage to semantically equivalent clauses that use non-standard language. A clause titled "data deletion upon request" can match to `gdpr_art_17` (Right to Erasure) even without using the article number.

**Evidential** — G3 precedent traversal grounds every gap in a real enforcement case. Art. 35 (DPIA) is not flagged as a gap with a generic warning. It is flagged with the Meta Ireland enforcement case (€17M, DPC 2022) as direct evidence that regulators enforce this obligation.

---

## 8. Risk Scoring

Risks are severity-graded on a four-level scale: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.

The default severity of each requirement comes from `gdpr_requirements.json` and reflects:
- Maximum penalty tier (Art. 83(4) vs Art. 83(5))
- Enforcement frequency in the knowledge graph
- Whether the obligation is procedural (MEDIUM) or substantive (CRITICAL/HIGH)

The `authority_score` on `Case` nodes is a normalized float encoding:
- DPA tier (lead supervisory authority vs. local DPA)
- Penalty magnitude relative to GDPR maximums
- Recency (post-Schrems II decisions weighted higher)

---

## 9. Fallback Modes

| Failure | Fallback |
|---|---|
| Groq API timeout | `_fallback()` — deterministic synthesis from retrieval bundle |
| Groq tool-use parse error | Same fallback |
| Embedding model unavailable | Vector results silently set to `[]`; graph results carry full weight |
| Contract not in graph | 404 from API; frontend shows empty state |
| ChromaDB query fails | Try/except in retrieval; vector units set to `[]` |

No failure mode leaves the user with an empty or crashed UI.

---

## 10. Data Model — GDPR Seed Data

The knowledge graph is seeded from `data/requirements/gdpr_requirements.json`:

**Framework:** GDPR 2016/679 (EU Data Protection Regulation)

**11 Requirements modeled:**
Art. 5 (Principles), Art. 6 (Lawfulness), Art. 13 (Transparency), Art. 17 (Right to Erasure),
Art. 25 (Privacy by Design), Art. 28 (Processor Obligations), Art. 30 (Records),
Art. 33 (Breach Notification), Art. 35 (DPIA), Art. 44 (Transfer Safeguards), Art. 83 (Penalties)

**9 Enforcement Cases:**
Meta Ireland (€1.2B, DPC 2023), Meta Ireland (€17M, DPC 2022), WhatsApp Ireland (€225M, DPC 2021),
Twitter International (€450K, DPC 2022), Amazon Europe (€746M, CNPD 2021),
Austrian Post (€18M, DSB 2023), H&M (€35M, HmbBfDI 2020), Google Spain (€600K, AEPD 2021),
Clearview AI (€20M, CNIL 2022)

**Two Contracts:**
- `nexus_meridian` — 10 clauses, 4 deliberate gaps (Art. 17, 25, 35, 44)
- `orion_payments` — 10 clauses, 0 gaps (control/comparison contract)
