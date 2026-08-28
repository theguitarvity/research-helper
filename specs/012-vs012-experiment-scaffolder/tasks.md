# Tasks: Experiment Scaffolder

- [ ] T001 `research_helper/experiments.py`: `EXPERIMENT_SUBDIRS` (FR-001)
- [ ] T002 `_next_experiment_id(paths) -> str` (FR-003)
- [ ] T003 `init_experiment(paths, name, *, title=None,
      research_question=None, hypothesis=None, independent=None,
      dependent=None, controlled=None, dataset=None, environment=None,
      reproduction_command=None, llm=None) -> Path` (FR-001, FR-002, FR-004, FR-005)
- [ ] T004 `research_helper/cli.py`: `experiment init <name>` command
- [ ] T010 `tests/test_experiments.py::test_init_creates_full_structure` (SC-001)
- [ ] T011 `tests/test_experiments.py::test_manifest_roundtrip` (SC-002)
- [ ] T012 `tests/test_experiments.py::test_no_llm_section_when_not_supplied` (SC-003)
- [ ] T013 `tests/test_experiments.py::test_sequential_ids`
- [ ] T014 `tests/test_experiments.py::test_reinit_is_idempotent`
