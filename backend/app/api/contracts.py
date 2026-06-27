"""Contract ingestion and listing endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.database.neo4j_client import get_neo4j
from app.database.chroma_client import get_chroma
from app.graph.ingestion import ingest_contract
from app.graph.queries import fetch_contract_summary, list_contracts
from app.rag.embedder import embed_and_upsert_clauses
from app.schemas.contract import ContractIn, ContractOut, ContractSummary

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.get("", response_model=list[ContractSummary])
async def list_all_contracts():
    import traceback
    try:
        neo4j = await get_neo4j()
        return await list_contracts(neo4j)
    except Exception as exc:
        raise HTTPException(status_code=500, detail={
            "error": str(exc),
            "type": type(exc).__name__,
            "trace": traceback.format_exc(),
        })


@router.get("/{contract_id}", response_model=ContractSummary)
async def get_contract(contract_id: str):
    neo4j = await get_neo4j()
    summary = await fetch_contract_summary(neo4j, contract_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return summary


@router.post("/ingest", response_model=ContractOut)
async def ingest(contract: ContractIn):
    neo4j = await get_neo4j()
    chroma = get_chroma()

    clause_count = await ingest_contract(neo4j, contract)

    clause_dicts = [
        {
            "clause_id": cl.clause_id,
            "contract_id": contract.contract_id,
            "section": cl.section,
            "text": cl.text,
        }
        for cl in contract.clauses
    ]
    try:
        await embed_and_upsert_clauses(chroma, clause_dicts)
    except Exception:
        pass

    return ContractOut(
        contract_id=contract.contract_id,
        clause_count=clause_count,
        ingested_at=datetime.now(timezone.utc),
    )
