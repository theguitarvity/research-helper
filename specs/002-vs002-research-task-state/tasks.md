# Tasks: Research Task + State

- [ ] T001 [US1] `research_helper/tasks.py`: `ResearchTask` Pydantic model
      (FR-001)
- [ ] T002 [US1] `_next_task_id(paths) -> str`: scan
      `.agent/state/tasks/*.json`, return next `RT-NNN`
- [ ] T003 [US1] `create_task(paths, type, objective, inputs=None,
      steps=None, agent="unknown") -> ResearchTask` (FR-002)
- [ ] T004 [US1] `load_active_task(paths) -> ResearchTask | None` (FR-003)
- [ ] T005 [US2] `record_agent_touch(paths, agent) -> ResearchTask`
      (FR-004), raises `LookupError` if no active task
- [ ] T006 [US1] `start_session(paths, agent) -> dict` (FR-005)
- [ ] T010 `tests/test_tasks.py::test_create_and_reload_task` (SC-001)
- [ ] T011 `tests/test_tasks.py::test_record_agent_touch_appends_history` (SC-002)
- [ ] T012 `tests/test_tasks.py::test_record_agent_touch_dedupes_consecutive`
- [ ] T013 `tests/test_tasks.py::test_load_active_task_none_when_absent`
- [ ] T014 `tests/test_tasks.py::test_record_agent_touch_without_active_task_raises`
- [ ] T015 `tests/test_tasks.py::test_second_task_keeps_first_addressable`
