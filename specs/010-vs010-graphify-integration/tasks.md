# Tasks: Graphify Integration

- [ ] T001 `research_helper/graph.py`: `GraphNode`, `GraphEdge`,
      `CitationGraph` models (FR-001)
- [ ] T002 `build_graph(paths) -> CitationGraph` scans library, builds
      Paper nodes + CITES edges (FR-002, FR-003, FR-004)
- [ ] T003 write `graph/citation-graph.json` (FR-005)
- [ ] T004 `find_seminal_papers(graph, top_n=5) -> list[tuple[str,int]]` (FR-006)
- [ ] T005 `find_isolated_nodes(graph, node_type=None) -> list[str]` (FR-006)
- [ ] T006 `research_helper/cli.py`: `graph build` command
- [ ] T010 `tests/test_graph.py::test_build_graph_links_cites_edges` (SC-001)
- [ ] T011 `tests/test_graph.py::test_build_graph_idempotent` (SC-002)
- [ ] T012 `tests/test_graph.py::test_find_seminal_papers_ranks_by_citations`
- [ ] T013 `tests/test_graph.py::test_find_isolated_nodes`
- [ ] T014 `tests/test_graph.py::test_doi_match_reuses_existing_node_no_duplicate`
