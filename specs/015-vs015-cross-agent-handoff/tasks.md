# Tasks: Cross-Agent Handoff

- [ ] T001 `research_helper/handoff.py`: `HandoffRecord` model (FR-001)
- [ ] T002 `render_handoff_md(record) -> str` §16 section order
- [ ] T003 `create_handoff(paths, *, agent, ...) -> HandoffRecord` (FR-002, FR-003)
- [ ] T004 `resume(paths) -> HandoffRecord | None` (FR-004)
- [ ] T005 `research_helper/cli.py`: `handoff create` and `resume` commands
- [ ] T010 `tests/test_handoff.py::test_handoff_md_has_all_sections` (SC-001)
- [ ] T011 `tests/test_handoff.py::test_handoff_json_roundtrip` (SC-002)
- [ ] T012 `tests/test_handoff.py::test_create_then_resume_round_trip` (SC-003)
- [ ] T013 `tests/test_handoff.py::test_resume_returns_none_when_absent`
