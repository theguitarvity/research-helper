# Feature Specification: Cross-Agent Handoff

**Feature dir**: `015-vs015-cross-agent-handoff` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 15 (VS015); `fundactional.md` §16-17

## Design note

§17 explicitly calls `handoff.json`'s schema "conceptual" (extensible),
and §16's Markdown template has sections (`What Was Done`, `Files
Changed`, `Assumptions`, `Known Problems`, `Reproduction Commands`) that
the minimal §17 JSON example doesn't list. To satisfy "`handoff.md` and
`handoff.json` never diverge on the facts they both represent," this
slice defines **one** `HandoffRecord` model that is the union of both
sections/fields — both files are rendered from the same record, so
nothing in one is silently absent from the other. *(INFERRED, extending
§17's schema as its own text invites)*

## User Scenarios & Testing

### User Story 1 - Create a full handoff record (P1)

**Acceptance Scenarios**:

1. **Given** an active Research Task and agent-supplied handoff details,
   **When** `create_handoff` runs, **Then** `handoff.md` has every §16
   section and `handoff.json` has every corresponding field, both
   derived from the same `HandoffRecord`.

### User Story 2 - Resume without chat history (P1)

**Acceptance Scenarios**:

1. **Given** a handoff was created, **When** the in-memory state is
   discarded (simulating a fresh agent/process) and `resume` is called,
   **Then** the returned record's objective, task, open questions, and
   next actions match what was created — reconstructed purely from disk.

## Requirements

### Functional Requirements

- **FR-001**: `HandoffRecord` MUST include every §16 Markdown section and
  every §17 JSON field as one unioned schema.
- **FR-002**: `create_handoff(paths, *, agent, ...)` MUST pull `task`/
  `objective` from the active `ResearchTask` (VS002) when one exists.
- **FR-003**: `create_handoff` MUST write both `.agent/state/handoff.md`
  (rendered, human-readable, §16 section order) and
  `.agent/state/handoff.json` (machine-readable) from the same record —
  single source, two renderings.
- **FR-004**: `resume(paths)` MUST read `handoff.json` and return the
  identical `HandoffRecord`, or `None` if no handoff exists yet.

## Success Criteria

- **SC-001**: `handoff.md` contains every §16 section heading.
- **SC-002**: `handoff.json` round-trips to an identical `HandoffRecord`.
- **SC-003**: A full create→resume round trip (with the in-memory object
  discarded in between) reproduces the same objective/task/open-questions/
  next-actions.

## Assumptions

See Design note above (unioned `HandoffRecord`).
