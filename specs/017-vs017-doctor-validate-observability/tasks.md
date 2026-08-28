# Tasks: Doctor / Validation / Observability

- [ ] T001 `research_helper/doctor.py`: `DoctorReport` model, `run_doctor(paths=None)`,
      `render_doctor_report(report)` (FR-001)
- [ ] T002 `research_helper/validate.py`: `ValidationIssue` model + 10 gate
      functions + `validate(paths)` aggregator (FR-002, FR-003)
- [ ] T003 `research_helper/observability.py`: `log_event(...)` fixed
      keyword signature (FR-004)
- [ ] T004 `research_helper/config.py`: `global_config_dir(system=None)` (FR-005)
- [ ] T005 `scripts/bootstrap.py` + thin `bootstrap.sh`/`bootstrap.ps1` wrappers (FR-006)
- [ ] T006 `research_helper/cli.py`: `doctor` and `validate` commands
- [ ] T010 `tests/test_doctor.py::test_doctor_detects_python_and_git` (SC-001)
- [ ] T011 `tests/test_validate.py::test_all_ten_gates_flagged_on_broken_fixtures` (SC-002)
- [ ] T012 `tests/test_validate.py::test_clean_lab_has_zero_issues` (SC-002)
- [ ] T013 `tests/test_observability.py::test_log_event_rejects_arbitrary_kwargs` (SC-003)
- [ ] T014 `tests/test_observability.py::test_log_event_writes_jsonl_line`
- [ ] T015 `tests/test_config.py::test_global_config_dir_all_three_branches` (SC-004)
