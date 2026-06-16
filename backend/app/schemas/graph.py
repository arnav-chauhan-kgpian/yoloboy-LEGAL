"""Graph payload schemas for React Flow rendering."""
from typing import Literal, Any
from pydantic import BaseModel, Field


NodeType = Literal[
    "Contract", "Clause", "Requirement", "Case",
    "ComplianceFramework", "Risk", "Court", "Report",
]


class GraphNode(BaseModel):
    id: str
    type: NodeType
    label: str
    data: dict[str, Any] = Field(default_factory=dict)
    is_gap: bool = False


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    animated: bool = False
    data: dict[str, Any] = Field(default_factory=dict)


class GraphPayload(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    gap_node_ids: list[str] = Field(default_factory=list)
