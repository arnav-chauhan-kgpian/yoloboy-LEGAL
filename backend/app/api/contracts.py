"""Contract ingestion and listing endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.database.neo4j_client import get_neo4j
from app.database.chroma_client import get_chroma
from app.graph.ingestion import ingest_contract
from app.graph.queries import fetch_contract_summary, list_contracts
from app.rag.embedder import embed_and_upsert_clauses
from app.schemas.contract import ContractIn, ClauseIn, ContractOut, ContractSummary
from app.services.document_parser import extract_text, segment_clauses, make_contract_id
from app.services.clause_mapper import map_clauses_to_requirements

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.get("", response_model=list[ContractSummary])
async def list_all_contracts():
    neo4j = await get_neo4j()
    return await list_contracts(neo4j)


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


@router.post("/upload", response_model=ContractOut)
async def upload_contract(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    parties: str | None = Form(None),
    governing_law: str = Form("Unknown"),
    framework_id: str = Form("gdpr_2016_679"),
):
    """Upload a legal document (PDF/DOCX/TXT). Parses, segments, auto-maps to GDPR
    requirements via Groq, ingests into the graph. Returns the new contract_id."""
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    try:
        text = extract_text(file.filename or "document.txt", raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {e}")

    if len(text.strip()) < 100:
        raise HTTPException(
            status_code=400,
            detail="Document text too short — could not extract enough content (even after OCR).",
        )

    resolved_title = title or (file.filename or "Uploaded Contract").rsplit(".", 1)[0]
    contract_id = make_contract_id(resolved_title)
    parties_list = [p.strip() for p in (parties or "Party A,Party B").split(",") if p.strip()]

    clause_dicts = segment_clauses(text, contract_id)
    if not clause_dicts:
        raise HTTPException(status_code=400, detail="Could not identify any clauses in the document.")

    neo4j = await get_neo4j()
    await map_clauses_to_requirements(neo4j, clause_dicts, framework_id)

    contract = ContractIn(
        contract_id=contract_id,
        title=resolved_title,
        parties=parties_list,
        governing_law=governing_law,
        framework_id=framework_id,
        clauses=[ClauseIn(**c) for c in clause_dicts],
    )

    clause_count = await ingest_contract(neo4j, contract)

    return ContractOut(
        contract_id=contract_id,
        clause_count=clause_count,
        ingested_at=datetime.now(timezone.utc),
    )
