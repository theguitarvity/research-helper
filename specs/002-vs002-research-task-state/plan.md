# Implementation Plan: Research Task + State

**Spec**: `./spec.md` | **Date**: 2026-08-27

## Summary

Add `research_helper.tasks`: a Pydantic `ResearchTask` model plus
functions to create/load/update it under `.agent/state/`, and a minimal
`start_session` helper for `.agent/state/session.json`.

## Technical Context

**Language/Version**: Python 3.12+ · **Primary Dependencies**: Pydantic
(model + JSON (de)serialization) · **Storage**: filesystem JSON under
`.agent/state/` · **Testing**: pytest with `LabPaths` over `tmp_path`

## Constitution Check

- Principle II (persistent artifacts): task state lives on disk, not in
  memory only. PASS.
- Principle I (model-agnostic): `agent` is a free-form string, no
  agent-specific branching. PASS.
- No new infra; filesystem-first. PASS.

## Project Structure

```text
research_helper/tasks.py
tests/test_tasks.py
```

**Structure decision**: sibling module to `lab.py`, depends only on
`LabPaths` for path resolution.
