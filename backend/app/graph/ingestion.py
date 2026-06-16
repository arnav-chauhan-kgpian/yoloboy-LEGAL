"""Ingest knowledge graph seed data into the in-memory GraphStore."""
from app.database.neo4j_client import GraphStore
from app.schemas.contract import ContractIn


async def init_constraints(store: GraphStore) -> None:
    pass  # No-op — in-memory store needs no schema constraints


async def ingest_framework(store: GraphStore, framework: dict) -> None:
    store.frameworks[framework["framework_id"]] = framework


async def ingest_requirements(
    store: GraphStore, framework_id: str, requirements: list[dict]
) -> int:
    if framework_id not in store.framework_requirements:
        store.framework_requirements[framework_id] = []
    for req in requirements:
        store.requirements[req["requirement_id"]] = req
        if req["requirement_id"] not in store.framework_requirements[framework_id]:
            store.framework_requirements[framework_id].append(req["requirement_id"])
    return len(requirements)


async def ingest_cases(store: GraphStore, cases: list[dict]) -> int:
    for case in cases:
        store.cases[case["case_id"]] = case
        court = case.get("court", {})
        if court.get("court_id"):
            store.courts[court["court_id"]] = court
        for req_id in case.get("enforces", []):
            if req_id not in store.req_enforced_by:
                store.req_enforced_by[req_id] = []
            if case["case_id"] not in store.req_enforced_by[req_id]:
                store.req_enforced_by[req_id].append(case["case_id"])
    return len(cases)


async def ingest_contract(store: GraphStore, contract: ContractIn) -> int:
    store.contracts[contract.contract_id] = {
        "contract_id": contract.contract_id,
        "title": contract.title,
        "parties": contract.parties,
        "governing_law": contract.governing_law,
        "data_categories": contract.data_categories,
    }
    store.contract_framework[contract.contract_id] = contract.framework_id
    store.contract_clauses[contract.contract_id] = []

    for idx, cl in enumerate(contract.clauses):
        store.clauses[cl.clause_id] = {
            "clause_id": cl.clause_id,
            "section": cl.section,
            "text": cl.text,
            "contract_id": contract.contract_id,
            "order": idx,
        }
        store.contract_clauses[contract.contract_id].append(cl.clause_id)
        store.clause_maps_to[cl.clause_id] = list(cl.maps_to_requirements)
        store.clause_conflicts[cl.clause_id] = list(cl.conflicts_with)
        store.clause_risks[cl.clause_id] = list(cl.risk_flags)

    return len(contract.clauses)
