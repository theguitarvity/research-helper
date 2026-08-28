# Tasks: Paper Import

- [ ] T001 `research_helper/papers.py`: `Provenance` model (FR-003)
- [ ] T002 `sha256_of(path) -> str` (FR-001)
- [ ] T003 `paper_identifier(doi, sha256) -> str` (FR-002)
- [ ] T004 [US1] [US2] `import_paper(...) -> Path` (FR-003, FR-004)
- [ ] T005 [US3] idempotency guard in `import_paper` (FR-005)
- [ ] T006 `research_helper/cli.py`: `import` command
- [ ] T010 `tests/test_papers.py::test_import_with_doi`
- [ ] T011 `tests/test_papers.py::test_import_without_doi_hash_fallback`
- [ ] T012 `tests/test_papers.py::test_reimport_is_idempotent`
- [ ] T013 `tests/test_papers.py::test_metadata_stub_never_fabricates_title`
