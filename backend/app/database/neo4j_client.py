"""In-memory property graph store — replaces Neo4j for zero-infrastructure operation."""
from __future__ import annotations


class GraphStore:
    """Lightweight in-memory property graph backed by Python dicts + adjacency lists."""

    def __init__(self) -> None:
        # Node stores
        self.contracts: dict[str, dict] = {}
        self.clauses: dict[str, dict] = {}
        self.requirements: dict[str, dict] = {}
        self.cases: dict[str, dict] = {}
        self.frameworks: dict[str, dict] = {}
        self.courts: dict[str, dict] = {}

        # Edge adjacency lists
        self.contract_clauses: dict[str, list[str]] = {}       # contract_id → [clause_id]
        self.clause_maps_to: dict[str, list[str]] = {}          # clause_id  → [req_id]
        self.clause_conflicts: dict[str, list[str]] = {}        # clause_id  → [req_id]
        self.clause_risks: dict[str, list[str]] = {}            # clause_id  → [risk_str]
        self.framework_requirements: dict[str, list[str]] = {}  # fw_id      → [req_id]
        self.req_enforced_by: dict[str, list[str]] = {}         # req_id     → [case_id]
        self.contract_framework: dict[str, str] = {}            # contract_id → fw_id

    def ping(self) -> bool:
        return True


# Alias keeps existing imports (orchestrator, health, etc.) working without changes
Neo4jClient = GraphStore

_store: GraphStore | None = None


async def get_neo4j() -> GraphStore:
    global _store
    if _store is None:
        _store = GraphStore()
    return _store


async def close_neo4j() -> None:
    global _store
    _store = None
