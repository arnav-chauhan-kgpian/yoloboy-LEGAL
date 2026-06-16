"""Agent result schemas — gaps, risks, citations."""
from typing import Literal
from pydantic import BaseModel, Field


Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]


class Citation(BaseModel):
    case_id: str
    case_name: str
    authority: str
    year: int
    penalty_eur: float | None = None
    holding: str
    authority_score: float = Field(ge=0.0, le=1.0)


class Gap(BaseModel):
    requirement_id: str
    article: str
    title: str
    severity: Severity
    rationale: str
    citation_anchors: list[str] = Field(default_factory=list)


class Risk(BaseModel):
    clause_id: str
    clause_section: str
    requirement_id: str
    article: str
    conflict_type: str
    severity: Severity
    rationale: str
    citation_anchors: list[str] = Field(default_factory=list)


class ContextUnit(BaseModel):
    anchor: str
    source_type: Literal["clause", "requirement", "case"]
    source_id: str
    text: str
    metadata: dict = Field(default_factory=dict)


class AgentResult(BaseModel):
    contract_id: str
    query: str
    gaps: list[Gap] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    summary: str = ""
    gap_count: int = 0
    risk_count: int = 0
