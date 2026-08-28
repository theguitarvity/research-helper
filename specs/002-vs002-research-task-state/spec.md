# Feature Specification: Research Task + State

**Feature dir**: `002-vs002-research-task-state` (trunk, no branch)

**Created**: 2026-08-27

**Status**: Draft

**Input**: `app-features.md` Feature 2 (VS002); `fundactional.md` §16, §17, §33, §45-47

## User Scenarios & Testing

### User Story 1 - Create an agent-independent Research Task (P1)

An agent starts working on a piece of research and records it as a
Research Task, so any other agent can later see what is being worked on
without reading chat history.

**Independent Test**: create a task with `research_helper.tasks.create_task`,
then load it back via a fresh call to `load_active_task` and assert every
field matches.

**Acceptance Scenarios**:

1. **Given** an initialized lab, **When** a task is created with a type,
   objective, and steps, **Then** it is persisted under `.agent/state/`
   with a stable `RT-NNN` id and is the lab's active task.
2. **Given** a lab with no task yet, **When** `load_active_task` is
   called, **Then** it returns `None` rather than raising.

---

### User Story 2 - Cross-agent history accumulates (P1)

A second agent picks up the active task and its name is added to the
task's history without erasing the first agent's contribution.

**Independent Test**: create a task as `claude`, call
`record_agent_touch(paths, "codex")`, reload the task, assert
`agent_history == ["claude", "codex"]`.

**Acceptance Scenarios**:

1. **Given** an active task created by agent A, **When** agent B touches
   it, **Then** `agent_history` contains both A and B, in the order they
   touched it, with no duplicate consecutive entries for the same agent
   touching it twice in a row.

### Edge Cases

- Creating a task when one is already active: the new task becomes the
  active task; the previous one remains retrievable by id under
  `.agent/state/tasks/` (no task is ever deleted by creating another).
- `record_agent_touch` called with no active task: raises a clear error
  (there is nothing to attribute the touch to) rather than silently
  creating one.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide a `ResearchTask` model with fields
  `id` (`RT-NNN`), `type`, `objective`, `inputs`, `status`, `steps`,
  `artifacts`, `agent_history`.
- **FR-002**: `create_task` MUST assign the next sequential `RT-NNN` id
  (based on existing task records, never reused), persist the task under
  `.agent/state/tasks/<id>.json`, and set it as the active task
  (`.agent/state/active-task.json`).
- **FR-003**: `load_active_task` MUST reconstruct the same `ResearchTask`
  from disk in a fresh process (no in-memory-only state).
- **FR-004**: `record_agent_touch` MUST append the touching agent to the
  active task's `agent_history` (skipping a no-op re-append if the same
  agent touches it twice consecutively) and persist the change to both
  the task record and the active-task pointer.
- **FR-005**: `start_session` MUST write `.agent/state/session.json` with
  a session id, start timestamp, and current agent — independent of any
  task.
- **FR-006**: Every write in this module MUST go through `LabPaths`
  (VS001) — no path segment is reconstructed manually.

### Key Entities

- **ResearchTask**: `RT-NNN`, agent-independent unit of research work.
- **Session**: ephemeral record of which agent is currently active and
  since when — distinct from a Research Task, which can outlive many
  sessions.

## Success Criteria

- **SC-001**: A task created by one process is fully reconstructed
  (all fields equal) by loading it in a separate process/instance.
- **SC-002**: `agent_history` never loses an entry across any number of
  `record_agent_touch` calls, including from concurrent-looking rapid
  sequential calls in a test.

## Assumptions

- Only one task is "active" per lab at a time (a stack/queue of tasks is
  not required by the acceptance criteria); older tasks remain addressable
  by id for later lineage work (VS016). *(INFERRED)*
