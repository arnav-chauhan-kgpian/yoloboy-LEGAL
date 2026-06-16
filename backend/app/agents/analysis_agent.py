"""Analysis Agent — produces citation-grounded gap and risk analysis using Groq."""
import json
import logging
from groq import AsyncGroq
from app.config import get_settings
from app.rag.retrieval import ContextBundle
from app.schemas.agent import AgentResult, Gap, Risk, Citation

log = logging.getLogger("lexgraph")

SYSTEM_PROMPT = """You are LexGraph's compliance analysis agent.

You receive a structured CONTEXT containing:
  - Contract clauses with [CTX_*] anchors
  - GDPR Requirements
  - Pre-detected GAPS (legally required obligations missing from the contract)
  - Pre-detected RISKS (clause-vs-requirement conflicts)
  - Enforcement CASES

You must produce a JSON object with exactly these fields:
  summary: A 2–3 sentence executive summary.
  gaps: One entry for each gap in CONTEXT.GAPS — do not invent gaps.
  risks: One entry for each risk in CONTEXT.RISKS — do not invent risks.
  citations: One entry for each case referenced — copy data verbatim.

CONSTRAINTS:
  * You may only make legal claims attributable to a [CTX_*] anchor in CONTEXT.
  * Every gap and risk MUST include citation_anchors (case_ids from CONTEXT).
  * Use exact field names. Severity values: CRITICAL, HIGH, MEDIUM, LOW.
  * Do not hallucinate case names, penalties, or article numbers.

Return ONLY via the emit_analysis tool — no prose, no markdown fences."""


TOOL = {
    "type": "function",
    "function": {
        "name": "emit_analysis",
        "description": "Emit the final compliance analysis result.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "gaps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "requirement_id": {"type": "string"},
                            "article": {"type": "string"},
                            "title": {"type": "string"},
                            "severity": {"type": "string"},
                            "rationale": {"type": "string"},
                            "citation_anchors": {
                                "type": "array", "items": {"type": "string"}
                            },
                        },
                        "required": ["requirement_id", "article", "title",
                                     "severity", "rationale", "citation_anchors"],
                    },
                },
                "risks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "clause_id": {"type": "string"},
                            "clause_section": {"type": "string"},
                            "requirement_id": {"type": "string"},
                            "article": {"type": "string"},
                            "conflict_type": {"type": "string"},
                            "severity": {"type": "string"},
                            "rationale": {"type": "string"},
                            "citation_anchors": {
                                "type": "array", "items": {"type": "string"}
                            },
                        },
                        "required": ["clause_id", "clause_section", "requirement_id",
                                     "article", "conflict_type", "severity",
                                     "rationale", "citation_anchors"],
                    },
                },
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "case_id": {"type": "string"},
                            "case_name": {"type": "string"},
                            "authority": {"type": "string"},
                            "year": {"type": "integer"},
                            "penalty_eur": {"type": ["number", "null"]},
                            "holding": {"type": "string"},
                            "authority_score": {"type": "number"},
                        },
                        "required": ["case_id", "case_name", "authority", "year",
                                     "holding", "authority_score"],
                    },
                },
            },
            "required": ["summary", "gaps", "risks", "citations"],
        },
    },
}


def _build_context_prompt(bundle: ContextBundle, query: str) -> str:
    lines = [f"USER_QUERY: {query}", "", "=== CONTEXT ==="]

    lines.append("\n--- CONTRACT CLAUSES ---")
    for u in bundle.units:
        if u.source_type == "clause":
            lines.append(f"[CTX_{u.source_id}] ({u.metadata.get('section','')}) {u.text}")

    lines.append("\n--- REQUIREMENTS REFERENCED ---")
    for u in bundle.units:
        if u.source_type == "requirement":
            lines.append(f"[CTX_{u.source_id}] {u.text}")

    lines.append("\n--- PRE-DETECTED GAPS (G2) ---")
    if not bundle.gaps:
        lines.append("(none)")
    for g in bundle.gaps:
        cases = g.get("cases", [])
        case_anchors = ", ".join(f"CTX_{c['case_id']}" for c in cases) or "(none)"
        lines.append(
            f"GAP: requirement_id={g['requirement_id']} "
            f"article={g.get('article')} title={g.get('title')} "
            f"severity={g.get('severity','CRITICAL')} "
            f"verbatim={g.get('verbatim_text','')[:200]} "
            f"supporting_cases=[{case_anchors}]"
        )

    lines.append("\n--- PRE-DETECTED RISKS (G1) ---")
    if not bundle.risks:
        lines.append("(none)")
    for r in bundle.risks:
        anchor = f"CTX_{r['case_id']}" if r.get("case_id") else "(none)"
        lines.append(
            f"RISK: clause_id={r['clause_id']} section={r.get('clause_section','')} "
            f"requirement_id={r['requirement_id']} article={r.get('article','')} "
            f"case={r.get('case_name','-')} penalty_eur={r.get('penalty_eur','-')} "
            f"supporting_case=[{anchor}]"
        )

    lines.append("\n--- CASES ---")
    seen = set()
    for u in bundle.units:
        if u.source_type == "case" and u.source_id not in seen:
            seen.add(u.source_id)
            md = u.metadata
            lines.append(
                f"[CTX_{u.source_id}] {md.get('name','')} "
                f"penalty_eur={md.get('penalty_eur')} "
                f"authority_score={md.get('authority_score')} "
                f"holding={u.text[:300]}"
            )

    lines.append("\n=== END CONTEXT ===")
    lines.append("Now emit the analysis via the emit_analysis tool.")
    return "\n".join(lines)


class AnalysisAgent:
    def __init__(self):
        settings = get_settings()
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    async def analyze(
        self, contract_id: str, query: str, bundle: ContextBundle
    ) -> AgentResult:
        prompt = _build_context_prompt(bundle, query)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                tools=[TOOL],
                tool_choice={"type": "function", "function": {"name": "emit_analysis"}},
                max_tokens=4096,
            )
        except Exception as e:
            log.warning(f"Groq call failed ({type(e).__name__}: {e}); using deterministic fallback.")
            return self._fallback(contract_id, query, bundle)

        try:
            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                return self._fallback(contract_id, query, bundle)
            payload = json.loads(tool_calls[0].function.arguments)
        except Exception as e:
            log.warning(f"Groq response parse failed ({e}); using deterministic fallback.")
            return self._fallback(contract_id, query, bundle)

        try:
            gaps = [Gap(**g) for g in payload.get("gaps", [])]
            risks = [Risk(**r) for r in payload.get("risks", [])]
            citations = [Citation(**c) for c in payload.get("citations", [])]
            return AgentResult(
                contract_id=contract_id,
                query=query,
                summary=payload.get("summary", ""),
                gaps=gaps,
                risks=risks,
                citations=citations,
                gap_count=len(gaps),
                risk_count=len(risks),
            )
        except Exception:
            return self._fallback(contract_id, query, bundle)

    def _fallback(
        self, contract_id: str, query: str, bundle: ContextBundle
    ) -> AgentResult:
        """Deterministic synthesis from retrieval bundle when model output fails."""
        gaps = []
        cites_seen: dict[str, Citation] = {}
        for g in bundle.gaps:
            cases = g.get("cases", [])
            anchors = [c["case_id"] for c in cases]
            gaps.append(Gap(
                requirement_id=g["requirement_id"],
                article=g.get("article", ""),
                title=g.get("title", ""),
                severity=g.get("severity", "CRITICAL"),
                rationale=(
                    f"This contract does not address {g.get('article','this requirement')}: "
                    f"{g.get('title','')}. {g.get('verbatim_text','')[:200]}"
                ),
                citation_anchors=anchors,
            ))
            for c in cases:
                cites_seen[c["case_id"]] = Citation(
                    case_id=c["case_id"],
                    case_name=c.get("case_name", ""),
                    authority=c.get("authority", ""),
                    year=c.get("year", 2020),
                    penalty_eur=c.get("penalty_eur"),
                    holding=c.get("holding", ""),
                    authority_score=c.get("authority_score", 0.5),
                )

        risks = []
        for r in bundle.risks:
            anchors = [r["case_id"]] if r.get("case_id") else []
            risks.append(Risk(
                clause_id=r["clause_id"],
                clause_section=r.get("clause_section", ""),
                requirement_id=r["requirement_id"],
                article=r.get("article", ""),
                conflict_type="REQUIREMENT_CONFLICT",
                severity="HIGH",
                rationale=(
                    f"Clause {r.get('clause_section','')} conflicts with "
                    f"{r.get('article','')} ({r.get('req_title','')})."
                ),
                citation_anchors=anchors,
            ))
            if r.get("case_id") and r["case_id"] not in cites_seen:
                cites_seen[r["case_id"]] = Citation(
                    case_id=r["case_id"],
                    case_name=r.get("case_name", ""),
                    authority="",
                    year=2020,
                    penalty_eur=r.get("penalty_eur"),
                    holding="",
                    authority_score=0.7,
                )

        summary = (
            f"Analysis identified {len(gaps)} legally required obligations missing "
            f"from this contract and {len(risks)} clause-level conflicts with GDPR."
        )

        return AgentResult(
            contract_id=contract_id,
            query=query,
            summary=summary,
            gaps=gaps,
            risks=risks,
            citations=list(cites_seen.values()),
            gap_count=len(gaps),
            risk_count=len(risks),
        )
