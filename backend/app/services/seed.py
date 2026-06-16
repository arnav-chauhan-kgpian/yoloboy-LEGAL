"""Seed the in-memory graph store and ChromaDB from data/ JSON files on startup."""
import asyncio
import json
from pathlib import Path
from app.config import get_settings
from app.database.neo4j_client import get_neo4j
from app.database.chroma_client import get_chroma
from app.graph.ingestion import (
    init_constraints, ingest_framework,
    ingest_requirements, ingest_cases, ingest_contract,
)
from app.rag.embedder import embed_and_upsert_clauses
from app.schemas.contract import ContractIn


def _data_root() -> Path:
    return Path(get_settings().data_path)


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def run_seed():
    root = _data_root()
    store = await get_neo4j()
    chroma = get_chroma()

    print(f"[seed] Data root: {root.resolve()}")

    await init_constraints(store)

    frameworks_path = root / "requirements" / "gdpr_requirements.json"
    data = _load_json(frameworks_path)

    fw = data["framework"]
    print(f"[seed] Ingesting framework: {fw['framework_id']}")
    await ingest_framework(store, fw)

    reqs = data["requirements"]
    print(f"[seed] Ingesting {len(reqs)} requirements...")
    await ingest_requirements(store, fw["framework_id"], reqs)

    cases = data.get("cases", [])
    print(f"[seed] Ingesting {len(cases)} enforcement cases...")
    await ingest_cases(store, cases)

    contracts_dir = root / "contracts"
    for contract_file in sorted(contracts_dir.glob("*.json")):
        print(f"[seed] Ingesting contract: {contract_file.name}")
        cdata = _load_json(contract_file)
        contract = ContractIn(**cdata)
        await ingest_contract(store, contract)

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
            print(f"[seed]   -> embedded {len(clause_dicts)} clauses")
        except Exception as e:
            print(f"[seed]   -> embedding skipped: {e}")

    print("[seed] Done.")


if __name__ == "__main__":
    asyncio.run(run_seed())
