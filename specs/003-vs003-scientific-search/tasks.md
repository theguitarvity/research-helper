# Tasks: Scientific Search

- [ ] T001 `research_helper/search.py`: `SearchResult`, `SearchQuery` models (FR-001)
- [ ] T002 `research_helper/search.py`: `SearchClient` Protocol (FR-002)
- [ ] T003 [US1] `dedup(results) -> list[SearchResult]` (FR-003)
- [ ] T004 [US2] `run_search(paths, query, clients) -> list[SearchResult]`
      writes manifest (FR-004, FR-005)
- [ ] T005 `research_helper/search_clients.py`: `SemanticScholarClient`,
      `CrossrefClient`, `OpenAlexClient` (FR-006)
- [ ] T006 `research_helper/cli.py`: `search` command (`--from/--to/--format`)
- [ ] T010 `tests/test_search.py::test_dedup_by_doi`
- [ ] T011 `tests/test_search.py::test_dedup_by_title_then_authors_year`
- [ ] T012 `tests/test_search.py::test_run_search_writes_full_manifest`
- [ ] T013 `tests/test_search.py::test_run_search_survives_one_client_failure`
- [ ] T014 `tests/test_search.py::test_query_yaml_roundtrip`
- [ ] T020 `tests/test_search_clients.py::test_semantic_scholar_client_parses_fixture` (respx)
- [ ] T021 `tests/test_search_clients.py::test_crossref_client_parses_fixture` (respx)
- [ ] T022 `tests/test_search_clients.py::test_openalex_client_parses_fixture` (respx)
