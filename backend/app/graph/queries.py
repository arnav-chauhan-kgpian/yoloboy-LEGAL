"""Graph queries — G1 coverage, G2 gap detection, G3 precedent chain (in-memory)."""
from app.database.neo4j_client import GraphStore
from app.schemas.graph import GraphPayload, GraphNode, GraphEdge
from app.schemas.contract import ContractSummary


async def g1_coverage_mapping(store: GraphStore, contract_id: str) -> list[dict]:
    rows = []
    for cl_id in store.contract_clauses.get(contract_id, []):
        cl = store.clauses.get(cl_id, {})
        for req_id in store.clause_conflicts.get(cl_id, []):
            req = store.requirements.get(req_id, {})
            case_ids = store.req_enforced_by.get(req_id, [])
            if case_ids:
                for cid in case_ids:
                    c = store.cases.get(cid, {})
                    rows.append({
                        "clause_id": cl_id,
                        "clause_section": cl.get("section", ""),
                        "clause_text": cl.get("text", ""),
                        "requirement_id": req_id,
                        "article": req.get("article", ""),
                        "req_title": req.get("title", ""),
                        "case_id": c.get("case_id"),
                        "case_name": c.get("name"),
                        "penalty_eur": c.get("penalty_eur"),
                        "authority_score": c.get("authority_score"),
                        "holding": c.get("holding"),
                    })
            else:
                rows.append({
                    "clause_id": cl_id,
                    "clause_section": cl.get("section", ""),
                    "clause_text": cl.get("text", ""),
                    "requirement_id": req_id,
                    "article": req.get("article", ""),
                    "req_title": req.get("title", ""),
                    "case_id": None,
                    "case_name": None,
                    "penalty_eur": None,
                    "authority_score": None,
                    "holding": None,
                })
    return rows


async def g2_gap_detection(
    store: GraphStore, contract_id: str, framework_id: str
) -> dict:
    all_req_ids = set(store.framework_requirements.get(framework_id, []))
    if not all_req_ids:
        return {
            "gap_requirements": [], "covered_requirements": [],
            "total": 0, "covered_count": 0, "gap_count": 0,
        }
    covered_ids: set[str] = set()
    for cl_id in store.contract_clauses.get(contract_id, []):
        covered_ids |= set(store.clause_maps_to.get(cl_id, []))
    gap_ids = all_req_ids - covered_ids

    def _req_dict(rid: str) -> dict:
        r = store.requirements.get(rid, {"requirement_id": rid})
        return {
            "requirement_id": rid,
            "article": r.get("article", ""),
            "title": r.get("title", ""),
            "severity": r.get("default_severity", "CRITICAL"),
            "verbatim_text": r.get("verbatim_text", ""),
        }

    return {
        "gap_requirements": [_req_dict(rid) for rid in gap_ids],
        "covered_requirements": [_req_dict(rid) for rid in covered_ids],
        "total": len(all_req_ids),
        "covered_count": len(covered_ids),
        "gap_count": len(gap_ids),
    }


async def g3_precedent_chain(store: GraphStore, requirement_id: str) -> list[dict]:
    rows = []
    for cid in store.req_enforced_by.get(requirement_id, []):
        c = store.cases.get(cid, {})
        rows.append({
            "case_id": cid,
            "case_name": c.get("name", ""),
            "authority": c.get("authority", ""),
            "year": c.get("year"),
            "penalty_eur": c.get("penalty_eur"),
            "holding": c.get("holding", ""),
            "authority_score": c.get("authority_score", 0.0),
            "court_name": None,
        })
    return sorted(rows, key=lambda x: -(x.get("authority_score") or 0))[:5]


async def fetch_base_graph(
    store: GraphStore,
    contract_id: str,
    framework_id: str = "gdpr_2016_679",
    include_gaps: bool = False,
) -> GraphPayload:
    contract = store.contracts.get(contract_id)
    if not contract:
        return GraphPayload()

    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    nodes[contract_id] = GraphNode(
        id=contract_id,
        type="Contract",
        label=contract.get("title", contract_id),
        data=contract,
    )

    for cl_id in store.contract_clauses.get(contract_id, []):
        cl = store.clauses.get(cl_id, {})
        nodes[cl_id] = GraphNode(
            id=cl_id,
            type="Clause",
            label=cl.get("section", cl_id),
            data=cl,
        )
        edges.append(GraphEdge(
            id=f"{contract_id}__HAS__{cl_id}",
            source=contract_id,
            target=cl_id,
            type="HAS_CLAUSE",
        ))

        for req_id in store.clause_maps_to.get(cl_id, []):
            req = store.requirements.get(req_id, {"requirement_id": req_id})
            if req_id not in nodes:
                nodes[req_id] = GraphNode(
                    id=req_id,
                    type="Requirement",
                    label=req.get("article", req_id),
                    data=req,
                )
            edges.append(GraphEdge(
                id=f"{cl_id}__MAPS_TO__{req_id}",
                source=cl_id,
                target=req_id,
                type="MAPS_TO",
            ))

        for req_id in store.clause_conflicts.get(cl_id, []):
            req = store.requirements.get(req_id, {"requirement_id": req_id})
            if req_id not in nodes:
                nodes[req_id] = GraphNode(
                    id=req_id,
                    type="Requirement",
                    label=req.get("article", req_id),
                    data=req,
                )
            edges.append(GraphEdge(
                id=f"{cl_id}__CONFLICTS_WITH__{req_id}",
                source=cl_id,
                target=req_id,
                type="CONFLICTS_WITH",
                animated=True,
            ))
            for cid in store.req_enforced_by.get(req_id, []):
                c = store.cases.get(cid, {})
                if cid not in nodes:
                    nodes[cid] = GraphNode(
                        id=cid,
                        type="Case",
                        label=c.get("name", cid),
                        data=c,
                    )
                e_id = f"{cid}__ENFORCED_BY__{req_id}"
                if not any(e.id == e_id for e in edges):
                    edges.append(GraphEdge(
                        id=e_id,
                        source=cid,
                        target=req_id,
                        type="ENFORCED_BY",
                    ))

    gap_ids: list[str] = []
    if include_gaps:
        gap_result = await g2_gap_detection(store, contract_id, framework_id)
        for gap in gap_result.get("gap_requirements", []):
            rid = gap["requirement_id"]
            gap_ids.append(rid)
            nodes[rid] = GraphNode(
                id=rid,
                type="Requirement",
                label=gap.get("article", rid),
                data={
                    "article": gap.get("article"),
                    "title": gap.get("title"),
                    "severity": gap.get("severity", "CRITICAL"),
                    "verbatim_text": gap.get("verbatim_text", ""),
                },
                is_gap=True,
            )

    return GraphPayload(
        nodes=list(nodes.values()),
        edges=edges,
        gap_node_ids=gap_ids,
    )


async def fetch_contract_summary(
    store: GraphStore, contract_id: str
) -> ContractSummary | None:
    c = store.contracts.get(contract_id)
    if not c:
        return None
    return ContractSummary(
        contract_id=c["contract_id"],
        title=c.get("title", ""),
        parties=c.get("parties", []),
        governing_law=c.get("governing_law", ""),
        clause_count=len(store.contract_clauses.get(contract_id, [])),
    )


async def list_contracts(store: GraphStore) -> list[ContractSummary]:
    result = []
    for cid, c in store.contracts.items():
        result.append(ContractSummary(
            contract_id=c["contract_id"],
            title=c.get("title", ""),
            parties=c.get("parties", []),
            governing_law=c.get("governing_law", ""),
            clause_count=len(store.contract_clauses.get(cid, [])),
        ))
    return sorted(result, key=lambda x: x.contract_id)
