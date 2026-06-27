"""Map uploaded contract clauses to GDPR requirements using Groq."""
from __future__ import annotations
import json
import logging
from groq import AsyncGroq
from app.config import get_settings
from app.database.neo4j_client import GraphStore

log = logging.getLogger("lexgraph")


def _requirement_catalog(store: GraphStore, framework_id: str) -> list[dict]:
    out = []
    for rid in store.framework_requirements.get(framework_id, []):
        r = store.requirements.get(rid, {})
        out.append({
            "requirement_id": rid,
            "article": r.get("article", ""),
            "title": r.get("title", ""),
        })
    return out


async def map_clauses_to_requirements(
    store: GraphStore,
    clauses: list[dict],
    framework_id: str = "gdpr_2016_679",
) -> list[dict]:
    """Annotate each clause with maps_to_requirements via a single Groq call.
    Falls back to empty mapping if Groq is unavailable — gap detection still works
    (every requirement becomes a gap, which is the correct conservative default)."""
    settings = get_settings()
    catalog = _requirement_catalog(store, framework_id)

    if not settings.groq_api_key or not catalog:
        for c in clauses:
            c.setdefault("maps_to_requirements", [])
            c.setdefault("conflicts_with", [])
            c.setdefault("risk_flags", [])
        return clauses

    catalog_str = "\n".join(
        f"- {r['requirement_id']} ({r['article']}): {r['title']}" for r in catalog
    )
    clause_str = "\n".join(
        f"[{i + 1}] {c['section']}\n{c['text'][:600]}" for i, c in enumerate(clauses)
    )

    prompt = f"""You are a legal compliance classifier. Map each contract clause to the GDPR
requirements it ADDRESSES (i.e., the clause attempts to satisfy that obligation).
Only assign a requirement if the clause text clearly relates to it. An empty list is
acceptable when no requirement applies.

REQUIREMENTS:
{catalog_str}

CLAUSES:
{clause_str}

Respond with ONLY a JSON object of the form:
{{"mappings": [{{"clause_index": 1, "requirement_ids": ["gdpr_art_5", ...]}}, ...]}}
"""

    try:
        client = AsyncGroq(api_key=settings.groq_api_key)
        resp = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)
        valid_ids = {r["requirement_id"] for r in catalog}
        mapping: dict[int, list[str]] = {}
        for m in data.get("mappings", []):
            idx = int(m.get("clause_index", 0))
            ids = [r for r in m.get("requirement_ids", []) if r in valid_ids]
            mapping[idx] = ids
        for i, c in enumerate(clauses, 1):
            c["maps_to_requirements"] = mapping.get(i, [])
            c.setdefault("conflicts_with", [])
            c.setdefault("risk_flags", [])
    except Exception as e:
        log.warning("Clause mapping failed (%s) — treating all requirements as gaps", e)
        for c in clauses:
            c.setdefault("maps_to_requirements", [])
            c.setdefault("conflicts_with", [])
            c.setdefault("risk_flags", [])

    return clauses
