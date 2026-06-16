"""Contract input/output schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ClauseIn(BaseModel):
    clause_id: str
    section: str
    text: str
    maps_to_requirements: list[str] = Field(default_factory=list)
    conflicts_with: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class ContractIn(BaseModel):
    contract_id: str
    title: str
    parties: list[str]
    governing_law: str
    data_categories: list[str] = Field(default_factory=list)
    framework_id: str = "gdpr_2016_679"
    clauses: list[ClauseIn]


class ContractOut(BaseModel):
    contract_id: str
    clause_count: int
    ingested_at: datetime


class ContractSummary(BaseModel):
    contract_id: str
    title: str
    parties: list[str]
    governing_law: str
    clause_count: int
