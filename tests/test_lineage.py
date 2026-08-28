import pytest

from research_helper import lab
from research_helper.lineage import (
    LineageGraph,
    add_edge,
    add_node,
    load_lineage,
    save_lineage,
    trace_back,
)


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def build_chain() -> LineageGraph:
    graph = LineageGraph()
    add_node(graph, "q1", "ResearchQuestion", "RESEARCHER_DECISION", text="Does X help?")
    add_node(graph, "p1", "Paper", "SOURCE_FACT", doi="10.1/x")
    add_node(graph, "c1", "Claim", "AGENT_INTERPRETATION", text="Paper claims X helps.")
    add_node(graph, "e1", "Experiment", "RESEARCHER_DECISION", id_="EXP-001")
    add_node(graph, "r1", "Result", "SOURCE_FACT", value="X improved by 12%")
    add_edge(graph, "q1", "p1")
    add_edge(graph, "p1", "c1")
    add_edge(graph, "c1", "e1")
    add_edge(graph, "e1", "r1")
    return graph


def test_trace_back_full_chain():
    graph = build_chain()

    chain = trace_back(graph, "r1")

    assert [n.id for n in chain] == ["r1", "e1", "c1", "p1", "q1"]


def test_add_edge_unknown_id_raises():
    graph = LineageGraph()
    add_node(graph, "q1", "ResearchQuestion", "RESEARCHER_DECISION")

    with pytest.raises(KeyError):
        add_edge(graph, "q1", "does-not-exist")


def test_invalid_classification_rejected():
    graph = LineageGraph()
    with pytest.raises(ValueError):
        add_node(graph, "x", "Paper", "MAYBE_TRUE")


def test_save_load_roundtrip(lab_paths):
    graph = build_chain()
    save_lineage(lab_paths, graph)

    reloaded = load_lineage(lab_paths)

    assert reloaded == graph


def test_load_lineage_empty_when_absent(lab_paths):
    assert load_lineage(lab_paths) == LineageGraph()
