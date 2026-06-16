"""Analysis request + SSE event schemas."""
from typing import Literal, Any
from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    contract_id: str
    query: str
    framework_id: str = "gdpr_2016_679"


EventType = Literal[
    "stage", "graph_data", "gaps", "risks",
    "citations", "synthesis_chunk", "complete", "error",
]


class SSEEvent(BaseModel):
    event: EventType
    data: dict[str, Any]
