# Tasks: Structured Paper Synthesis

- [ ] T001 `research_helper/synthesis.py`: `PaperSynthesis` model, 17
      optional fields in §11 order (FR-001)
- [ ] T002 `SECTION_TITLES` ordered list mapping field -> heading text
- [ ] T003 `render_synthesis(synthesis) -> str` (FR-002)
- [ ] T004 `write_individual_synthesis(paths, paper_id, synthesis) -> Path` (FR-003)
- [ ] T005 `write_comparative_synthesis(paths, **sections) -> dict[str, Path]` (FR-004)
- [ ] T006 `research_helper/cli.py`: `summarize <paper> --from-json <file>` command
- [ ] T010 `tests/test_synthesis.py::test_render_marks_unset_sections_not_defined` (SC-001)
- [ ] T011 `tests/test_synthesis.py::test_write_individual_synthesis_path`
- [ ] T012 `tests/test_synthesis.py::test_comparative_synthesis_always_writes_four_files` (SC-002)
