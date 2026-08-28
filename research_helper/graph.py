"""File-based, Graphify-shaped citation graph (VS010, `fundactional.md`
§12-13). No existing Graphify installation was found on this machine
(tech-stack.md); this ships a self-contained graph designed to be
consumed by a real integration later.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, Field

from research_helper.lab import LabPaths

LINKING_STATES = ("VERIFIED", "RESOLVED")


class GraphNode(BaseModel):
    id: str
    type: str
    properties: dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    properties: dict = Field(default_factory=dict)


class CitationGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


def _external_node_id(doi: str | None, raw_text: str) -> str:
    key = doi.strip().lower() if doi else raw_text
    return "ext-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def build_graph(paths: LabPaths) -> CitationGraph:
    """FR-002..FR-004: rebuilt fresh from source data every call."""
    nodes: dict[str, GraphNode] = {}
    doi_to_node_id: dict[str, str] = {}
    edges: list[GraphEdge] = []

    paper_dirs = sorted(
        (p for p in paths.library_papers_dir.iterdir() if p.is_dir()), key=lambda p: p.name
    )

    for paper_dir in paper_dirs:
        identifier = paper_dir.name
        manifest = _read_json(paper_dir / "manifest.json")
        metadata = _read_json(paper_dir / "metadata.json")
        doi = manifest.get("doi") if manifest else None
        title = metadata.get("title") if metadata else None
        properties = {k: v for k, v in {"doi": doi, "title": title}.items() if v}
        nodes[identifier] = GraphNode(id=identifier, type="Paper", properties=properties)
        if doi:
            doi_to_node_id[doi.strip().lower()] = identifier

    for paper_dir in paper_dirs:
        identifier = paper_dir.name
        resolved = _read_json_list(paper_dir / "references.resolved.json")
        for ref in sorted(resolved, key=lambda r: r.get("raw_text", "")):
            if ref.get("state") not in LINKING_STATES:
                continue
            doi = ref.get("doi")
            doi_key = doi.strip().lower() if doi else None

            if doi_key and doi_key in doi_to_node_id:
                target_id = doi_to_node_id[doi_key]
            else:
                target_id = _external_node_id(doi, ref.get("raw_text", ""))
                if target_id not in nodes:
                    properties = {
                        k: v
                        for k, v in {
                            "doi": doi,
                            "title": ref.get("title"),
                            "year": ref.get("year"),
                        }.items()
                        if v
                    }
                    nodes[target_id] = GraphNode(id=target_id, type="Paper", properties=properties)
                if doi_key:
                    doi_to_node_id[doi_key] = target_id

            edges.append(GraphEdge(source=identifier, target=target_id, type="CITES"))

    graph = CitationGraph(nodes=[nodes[k] for k in sorted(nodes)], edges=edges)
    dest = paths.graph_dir / "citation-graph.json"
    dest.write_text(graph.model_dump_json(indent=2), encoding="utf-8")
    return graph


def find_seminal_papers(graph: CitationGraph, top_n: int = 5) -> list[tuple[str, int]]:
    in_degree = Counter(edge.target for edge in graph.edges if edge.type == "CITES")
    ranked = sorted(
        ((node.id, in_degree.get(node.id, 0)) for node in graph.nodes if node.type == "Paper"),
        key=lambda pair: (-pair[1], pair[0]),
    )
    return ranked[:top_n]


def find_isolated_nodes(graph: CitationGraph, node_type: str | None = None) -> list[str]:
    touched = {e.source for e in graph.edges} | {e.target for e in graph.edges}
    return [
        node.id
        for node in graph.nodes
        if node.id not in touched and (node_type is None or node.type == node_type)
    ]


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json_list(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
