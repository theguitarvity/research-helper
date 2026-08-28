# Tasks: Reference Resolution

- [ ] T001 `research_helper/references.py`: `ResolvedReference` model
- [ ] T002 `extract_citation_year(raw_text) -> int | None`
- [ ] T003 `_title_similarity(a, b) -> float` (difflib)
- [ ] T004 `resolve_reference(ref, clients) -> ResolvedReference` (FR-001..005)
- [ ] T005 `resolve_references(paper_dir, clients) -> list[ResolvedReference]`
      writes `references.resolved.json` (FR-006, FR-007)
- [ ] T006 `to_bibtex(resolved_refs) -> str`, write `references.bib` (FR-006)
- [ ] T007 `research_helper/cli.py`: `references resolve <paper-id>` command
- [ ] T010 `tests/test_reference_resolution.py::test_exact_doi_match_is_verified` (SC-001)
- [ ] T011 `tests/test_reference_resolution.py::test_no_candidates_is_unavailable` (SC-002)
- [ ] T012 `tests/test_reference_resolution.py::test_year_mismatch_flagged` (SC-003)
- [ ] T013 `tests/test_reference_resolution.py::test_ambiguous_on_tied_candidates`
- [ ] T014 `tests/test_reference_resolution.py::test_bibtex_written_for_resolved_and_unavailable` (SC-004)
- [ ] T015 `tests/test_reference_resolution.py::test_client_failure_does_not_abort_resolution`
