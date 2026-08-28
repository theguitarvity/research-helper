# Tasks: LaTeX / Venue Scaffolder

- [ ] T001 `research_helper/lab.py`: `LabPaths.venues_dir` property
- [ ] T002 `research_helper/paper_project.py`: `BUILTIN_GENERIC_VENUE` (FR-002, FR-003)
- [ ] T003 `load_venue(paths, venue_name) -> dict` (FR-002)
- [ ] T004 `init_paper_project(paths, *, venue, name) -> Path` (FR-001, FR-004, FR-005)
- [ ] T005 `research_helper/cli.py`: `paper init --venue --name` command
- [ ] T010 `tests/test_paper_project.py::test_generic_venue_works_out_of_the_box` (SC-001)
- [ ] T011 `tests/test_paper_project.py::test_unregistered_venue_raises_with_expected_path` (SC-002)
- [ ] T012 `tests/test_paper_project.py::test_registered_venue_pinned_verbatim` (SC-003)
- [ ] T013 `tests/test_paper_project.py::test_structure_matches_section_19`
- [ ] T014 `tests/test_paper_project.py::test_reinit_is_idempotent`
