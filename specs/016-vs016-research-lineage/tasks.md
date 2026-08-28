# Tasks: Research Lineage

- [ ] T001 `research_helper/lineage.py`: `LineageNode`, `LineageEdge`,
      `LineageGraph` models (FR-001)
- [ ] T002 `add_node(graph, id, type, classification, **properties) -> LineageNode`
- [ ] T003 `add_edge(graph, source_id, target_id) -> LineageEdge` (FR-002)
- [ ] T004 `trace_back(graph, node_id) -> list[LineageNode]` (FR-003)
- [ ] T005 `save_lineage(paths, graph) -> Path`, `load_lineage(paths) ->
      LineageGraph` (FR-004)
- [ ] T010 `tests/test_lineage.py::test_trace_back_full_chain` (SC-001)
- [ ] T011 `tests/test_lineage.py::test_add_edge_unknown_id_raises` (SC-002)
- [ ] T012 `tests/test_lineage.py::test_invalid_classification_rejected` (SC-003)
- [ ] T013 `tests/test_lineage.py::test_save_load_roundtrip`
