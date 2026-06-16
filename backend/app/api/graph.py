"""Graph endpoints — return React Flow GraphPayload."""
from fastapi import APIRouter, HTTPException
from app.database.neo4j_client import get_neo4j
from app.graph.queries import fetch_base_graph, g2_gap_detection
from app.schemas.graph import GraphPayload

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/{contract_id}", response_model=GraphPayload)
async def get_graph(
    contract_id: str,
    include_gaps: bool = False,
    framework_id: str = "gdpr_2016_679",
):
    neo4j = await get_neo4j()
    payload = await fetch_base_graph(neo4j, contract_id, framework_id, include_gaps)
    if not payload.nodes:
        raise HTTPException(status_code=404, detail="Contract not found")
    return payload


@router.get("/{contract_id}/gaps")
async def get_gaps(contract_id: str, framework_id: str = "gdpr_2016_679"):
    neo4j = await get_neo4j()
    return await g2_gap_detection(neo4j, contract_id, framework_id)
