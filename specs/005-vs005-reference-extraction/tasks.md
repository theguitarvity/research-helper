# Tasks: Reference Extraction

- [ ] T001 Add `pypdf` to `pyproject.toml` dependencies
- [ ] T002 `research_helper/references.py`: `RawReference` model (FR-002)
- [ ] T003 `extract_text(pdf_path) -> str` via `pypdf` (FR-001)
- [ ] T004 `detect_references_section(text) -> str` (FR-003)
- [ ] T005 `split_references(section) -> list[str]` bracket/numbered/paragraph (FR-004)
- [ ] T006 `extract_doi(text) -> str | None` (FR-006)
- [ ] T007 `extract_references(paper_dir) -> list[RawReference]` writes
      raw+normalized JSON (FR-005)
- [ ] T008 `research_helper/cli.py`: `references extract <paper-id>` command
- [ ] T020 `tests/pdf_fixtures.py`: `make_pdf(lines) -> bytes` (hand-built,
      no new dependency)
- [ ] T021 `tests/test_references.py::test_extract_bracket_numbered_references` (SC-001)
- [ ] T022 `tests/test_references.py::test_extract_no_references_section` (SC-002)
- [ ] T023 `tests/test_references.py::test_extract_captures_embedded_doi` (SC-003)
- [ ] T024 `tests/test_references.py::test_extract_plain_numbered_references`
