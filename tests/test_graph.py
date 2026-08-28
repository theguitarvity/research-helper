import json

import pytest

from research_helper import lab
from research_helper.graph import build_graph, find_isolated_nodes, find_seminal_papers


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def make_paper(lab_paths, identifier, doi=None, title=None, resolved_refs=None):
    paper_dir = lab_paths.library_papers_dir / identifier
    paper_dir.mkdir(parents=True)
    (paper_dir / "manifest.json").write_text(json.dumps({"doi": doi}))
    (paper_dir / "metadata.json").write_text(json.dumps({"doi": doi, "title": title}))
    if resolved_refs is not None:
        (paper_dir / "references.resolved.json").write_text(json.dumps(resolved_refs))
    return paper_dir


def test_build_graph_links_cites_edges(lab_paths):
    make_paper(lab_paths, "paper-b", doi="10.1/b", title="Paper B")
    make_paper(lab_paths, "paper-c", doi="10.1/c", title="Paper C")
    make_paper(
        lab_paths,
        "paper-a",
        doi="10.1/a",
        title="Paper A",
        resolved_refs=[
            {"raw_text": "[1]", "doi": "10.1/b", "state": "VERIFIED"},
            {"raw_text": "[2]", "doi": "10.1/c", "state": "RESOLVED"},
        ],
    )

    graph = build_graph(lab_paths)

    node_ids = {n.id for n in graph.nodes}
    assert {"paper-a", "paper-b", "paper-c"} <= node_ids
    edge_pairs = {(e.source, e.target) for e in graph.edges}
    assert ("paper-a", "paper-b") in edge_pairs
    assert ("paper-a", "paper-c") in edge_pairs
    assert (lab_paths.graph_dir / "citation-graph.json").is_file()


def test_build_graph_idempotent(lab_paths):
    make_paper(
        lab_paths,
        "paper-a",
        doi="10.1/a",
        resolved_refs=[{"raw_text": "[1]", "doi": "10.1/x", "state": "VERIFIED"}],
    )

    build_graph(lab_paths)
    first = (lab_paths.graph_dir / "citation-graph.json").read_bytes()
    build_graph(lab_paths)
    second = (lab_paths.graph_dir / "citation-graph.json").read_bytes()

    assert first == second


def test_find_seminal_papers_ranks_by_citations(lab_paths):
    make_paper(lab_paths, "paper-e", doi="10.1/e")
    make_paper(
        lab_paths,
        "paper-b",
        doi="10.1/b",
        resolved_refs=[{"raw_text": "[1]", "doi": "10.1/e", "state": "VERIFIED"}],
    )
    make_paper(
        lab_paths,
        "paper-a",
        doi="10.1/a",
        resolved_refs=[
            {"raw_text": "[1]", "doi": "10.1/b", "state": "VERIFIED"},
            {"raw_text": "[2]", "doi": "10.1/c", "state": "VERIFIED"},
        ],
    )
    make_paper(
        lab_paths,
        "paper-c",
        doi="10.1/c",
        resolved_refs=[{"raw_text": "[1]", "doi": "10.1/e", "state": "VERIFIED"}],
    )

    graph = build_graph(lab_paths)
    ranked = find_seminal_papers(graph, top_n=3)

    assert ranked[0][0] == "paper-e"
    assert ranked[0][1] == 2


def test_find_isolated_nodes(lab_paths):
    make_paper(lab_paths, "paper-lonely", doi="10.1/lonely")
    make_paper(
        lab_paths,
        "paper-a",
        doi="10.1/a",
        resolved_refs=[{"raw_text": "[1]", "doi": "10.1/b", "state": "VERIFIED"}],
    )

    graph = build_graph(lab_paths)
    isolated = find_isolated_nodes(graph, node_type="Paper")

    assert "paper-lonely" in isolated
    assert "paper-a" not in isolated


def test_doi_match_reuses_existing_node_no_duplicate(lab_paths):
    make_paper(lab_paths, "paper-b", doi="10.1/b", title="Paper B")
    make_paper(
        lab_paths,
        "paper-a",
        doi="10.1/a",
        resolved_refs=[{"raw_text": "[1]", "doi": "10.1/b", "state": "VERIFIED"}],
    )

    graph = build_graph(lab_paths)
    b_nodes = [n for n in graph.nodes if n.properties.get("doi") == "10.1/b"]

    assert len(b_nodes) == 1
    assert b_nodes[0].id == "paper-b"
