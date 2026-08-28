"""Research lineage chain (VS016, `fundactional.md` §10, §37):
Research Question -> Literature Search -> Papers -> Claims -> Hypothesis
-> Experiment -> Evidence -> Result -> Paper Section.

`classification` is a required, single-valued field so a node can never
mix SOURCE_FACT / AGENT_INTERPRETATION / RESEARCHER_DECISION (§10,
"never mix these") — enforced structurally, not by convention.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from research_helper.lab import LabPaths

Classification = Literal["SOURCE_FACT", "AGENT_INTERPRETATION", "RESEARCHER_DECISION"]


class LineageNode(BaseModel):
    id: str
    type: str
    classification: Classification
    properties: dict = Field(default_factory=dict)


class LineageEdge(BaseModel):
    source: str
    target: str


class LineageGraph(BaseModel):
    nodes: list[LineageNode] = Field(default_factory=list)
    edges: list[LineageEdge] = Field(default_factory=list)


def add_node(
    graph: LineageGraph, id: str, type: str, classification: Classification, **properties
) -> LineageNode:
    node = LineageNode(id=id, type=type, classification=classification, properties=properties)
    graph.nodes = [n for n in graph.nodes if n.id != id] + [node]
    return node


def add_edge(graph: LineageGraph, source_id: str, target_id: str) -> LineageEdge:
    """FR-002: never link to a node that doesn't exist."""
    known_ids = {n.id for n in graph.nodes}
    for node_id in (source_id, target_id):
        if node_id not in known_ids:
            raise KeyError(f"Unknown lineage node id: {node_id!r}")
    edge = LineageEdge(source=source_id, target=target_id)
    graph.edges.append(edge)
    return edge


def trace_back(graph: LineageGraph, node_id: str) -> list[LineageNode]:
    """FR-003: walk backward (target -> source) to every ancestor, in order."""
    nodes_by_id = {n.id: n for n in graph.nodes}
    incoming: dict[str, str] = {e.target: e.source for e in graph.edges}

    chain: list[LineageNode] = []
    current = node_id
    visited: set[str] = set()
    while current in nodes_by_id and current not in visited:
        visited.add(current)
        chain.append(nodes_by_id[current])
        current = incoming.get(current, "")

    return chain


def save_lineage(paths: LabPaths, graph: LineageGraph) -> Path:
    dest = paths.graph_dir / "research-lineage.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(graph.model_dump_json(indent=2), encoding="utf-8")
    return dest


def load_lineage(paths: LabPaths) -> LineageGraph:
    dest = paths.graph_dir / "research-lineage.json"
    if not dest.is_file():
        return LineageGraph()
    return LineageGraph.model_validate_json(dest.read_text(encoding="utf-8"))
