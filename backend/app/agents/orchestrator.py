"""Orchestrator — routes the query through retrieval and analysis, emits SSE events."""
import json
from typing import AsyncIterator
from app.database.neo4j_client import Neo4jClient
from app.database.chroma_client import ChromaClient
from app.rag.retrieval import GraphRAGRetriever
from app.agents.analysis_agent import AnalysisAgent
from app.graph.queries import fetch_base_graph
from app.schemas.analysis import SSEEvent


def _format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


class OrchestratorAgent:
    def __init__(self, neo4j: Neo4jClient, chroma: ChromaClient):
        self.neo4j = neo4j
        self.chroma = chroma
        self.retriever = GraphRAGRetriever(neo4j, chroma)
        self.analyzer = AnalysisAgent()

    async def run(
        self, contract_id: str, query: str, framework_id: str
    ) -> AsyncIterator[str]:
        try:
            yield _format_sse("stage", {
                "stage": "routing",
                "message": "Routing query through orchestrator...",
            })

            yield _format_sse("stage", {
                "stage": "retrieving",
                "message": "Traversing legal knowledge graph (G1, G2, G3)...",
            })
            bundle = await self.retriever.retrieve(contract_id, query, framework_id)

            graph_payload = await fetch_base_graph(
                self.neo4j, contract_id, framework_id, include_gaps=True
            )
            yield _format_sse("graph_data", graph_payload.model_dump())

            yield _format_sse("stage", {
                "stage": "analyzing",
                "message": f"Found {bundle.gap_count} gaps, {len(bundle.risks)} risks. "
                           f"Running analysis agent...",
            })

            result = await self.analyzer.analyze(contract_id, query, bundle)

            if result.gaps:
                yield _format_sse("gaps", {
                    "gaps": [g.model_dump() for g in result.gaps]
                })
            if result.risks:
                yield _format_sse("risks", {
                    "risks": [r.model_dump() for r in result.risks]
                })
            if result.citations:
                yield _format_sse("citations", {
                    "citations": [c.model_dump() for c in result.citations]
                })

            yield _format_sse("synthesis_chunk", {"text": result.summary})

            yield _format_sse("complete", result.model_dump())

        except Exception as e:
            yield _format_sse("error", {
                "message": str(e),
                "type": type(e).__name__,
            })
