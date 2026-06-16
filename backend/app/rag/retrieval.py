"""GraphRAG retriever — fuses Neo4j graph traversal + Chroma vector search."""
from dataclasses import dataclass, field
from app.database.neo4j_client import Neo4jClient
from app.database.chroma_client import ChromaClient
from app.graph.queries import g1_coverage_mapping, g2_gap_detection, g3_precedent_chain
from app.rag.embedder import embed_query
from app.rag.rrf import reciprocal_rank_fusion
from app.schemas.agent import ContextUnit


@dataclass
class ContextBundle:
    units: list[ContextUnit] = field(default_factory=list)
    risks: list[dict] = field(default_factory=list)
    gaps: list[dict] = field(default_factory=list)
    covered: list[dict] = field(default_factory=list)
    gap_count: int = 0
    total_requirements: int = 0


class GraphRAGRetriever:
    def __init__(self, neo4j: Neo4jClient, chroma: ChromaClient):
        self.neo4j = neo4j
        self.chroma = chroma

    async def retrieve(
        self,
        contract_id: str,
        query: str,
        framework_id: str,
    ) -> ContextBundle:
        risks_raw = await g1_coverage_mapping(self.neo4j, contract_id)
        gap_result = await g2_gap_detection(self.neo4j, contract_id, framework_id)

        graph_units: list[dict] = []
        risks_seen: dict[str, dict] = {}
        for r in risks_raw:
            if r.get("clause_id"):
                anchor = f"clause::{r['clause_id']}"
                if anchor not in {u["anchor"] for u in graph_units}:
                    graph_units.append({
                        "anchor": anchor,
                        "source_type": "clause",
                        "source_id": r["clause_id"],
                        "text": r.get("clause_text", ""),
                        "metadata": {"section": r.get("clause_section")},
                    })
            if r.get("requirement_id"):
                anchor = f"requirement::{r['requirement_id']}"
                if anchor not in {u["anchor"] for u in graph_units}:
                    graph_units.append({
                        "anchor": anchor,
                        "source_type": "requirement",
                        "source_id": r["requirement_id"],
                        "text": f"{r.get('article','')} — {r.get('req_title','')}",
                        "metadata": {"article": r.get("article")},
                    })
            if r.get("case_id"):
                anchor = f"case::{r['case_id']}"
                if anchor not in {u["anchor"] for u in graph_units}:
                    graph_units.append({
                        "anchor": anchor,
                        "source_type": "case",
                        "source_id": r["case_id"],
                        "text": r.get("holding", ""),
                        "metadata": {
                            "name": r.get("case_name"),
                            "penalty_eur": r.get("penalty_eur"),
                            "authority_score": r.get("authority_score"),
                        },
                    })
            if r.get("clause_id") and r.get("requirement_id"):
                rid = r["requirement_id"]
                if rid not in risks_seen:
                    risks_seen[rid] = {
                        "clause_id": r["clause_id"],
                        "clause_section": r.get("clause_section", ""),
                        "requirement_id": rid,
                        "article": r.get("article", ""),
                        "req_title": r.get("req_title", ""),
                        "case_id": r.get("case_id"),
                        "case_name": r.get("case_name"),
                        "penalty_eur": r.get("penalty_eur"),
                    }

        vector_units: list[dict] = []
        try:
            qvec = await embed_query(query)
            if qvec:
                res = self.chroma.query(
                    query_embedding=qvec,
                    n_results=10,
                    where={"contract_id": contract_id},
                )
                ids = (res.get("ids") or [[]])[0]
                docs = (res.get("documents") or [[]])[0]
                metas = (res.get("metadatas") or [[]])[0]
                for cid, doc, meta in zip(ids, docs, metas):
                    vector_units.append({
                        "anchor": f"clause::{cid}",
                        "source_type": "clause",
                        "source_id": cid,
                        "text": doc,
                        "metadata": meta or {},
                    })
        except Exception:
            vector_units = []

        fused = reciprocal_rank_fusion(graph_units, vector_units)

        gap_dicts = gap_result.get("gap_requirements", []) or []
        for gap in gap_dicts:
            cases = await g3_precedent_chain(self.neo4j, gap["requirement_id"])
            gap["cases"] = cases
            for case in cases:
                anchor = f"case::{case['case_id']}"
                if not any(u["anchor"] == anchor for u in fused):
                    fused.append({
                        "anchor": anchor,
                        "source_type": "case",
                        "source_id": case["case_id"],
                        "text": case.get("holding", ""),
                        "metadata": {
                            "name": case.get("case_name"),
                            "penalty_eur": case.get("penalty_eur"),
                            "authority_score": case.get("authority_score"),
                        },
                    })

        units = [
            ContextUnit(
                anchor=u["anchor"],
                source_type=u["source_type"],
                source_id=u["source_id"],
                text=u["text"],
                metadata=u.get("metadata", {}),
            )
            for u in fused[:25]
        ]

        return ContextBundle(
            units=units,
            risks=list(risks_seen.values()),
            gaps=gap_dicts,
            covered=gap_result.get("covered_requirements", []) or [],
            gap_count=gap_result.get("gap_count", 0),
            total_requirements=gap_result.get("total", 0),
        )
