# Implementation Plan: Research Lab Foundation

**Feature dir**: `specs/001-vs001-research-lab-foundation` (trunk, no branch) | **Date**: 2026-08-27 | **Spec**: `./spec.md`

## Summary

Implement `research_helper.lab` (workspace resolution + scaffolding) and
wire `research-helper init [PATH]` in `research_helper.cli` (Typer). This
is also where the Python project itself (`pyproject.toml`, `uv` env,
`pytest` config) is bootstrapped, since no code exists yet.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Typer (CLI), Pydantic (not yet needed for this
slice's data — `research-helper.yaml` is plain YAML — but the dependency
is added now since VS002+ need it immediately), PyYAML

**Storage**: filesystem only (YAML manifest, directory tree)

**Testing**: pytest, using `tmp_path` fixture — no network, no real HOME
directory writes

**Target Platform**: macOS (this environment, live-tested); Windows/Linux/
Termux supported by construction (`pathlib` only) but not live-tested here

**Project Type**: single Python package + CLI

**Performance Goals**: N/A (filesystem scaffolding, not a hot path)

**Constraints**: no absolute/OS-specific path ever persisted (constitution
Principle VII); idempotent by construction

**Scale/Scope**: one lab per invocation; directory count is small and fixed

## Constitution Check

- Principle I (model-agnostic): CLI has no agent-specific behavior. PASS.
- Principle II (persistent artifacts): `research-helper.yaml` + directory
  tree *is* the persistent artifact this slice produces. PASS.
- Principle III (script-first): scaffolding is 100% deterministic Python,
  no LLM call. PASS.
- Principle VI (filesystem-first): no DB, no service. PASS.
- Principle VII (portability): `pathlib` exclusively; paths persisted
  relative to lab root. PASS — enforced by a dedicated unit test (SC-003).

No violations; no complexity to justify.

## Project Structure

```text
pyproject.toml
research_helper/
├── __init__.py
├── cli.py              # Typer app, `init` command
├── lab.py              # LabPaths, resolve_lab_root(), scaffold()
└── py.typed
tests/
├── conftest.py
├── test_lab.py
└── test_cli_init.py
```

**Structure decision**: single Python package at repo root (`research_helper/`),
CLI thin wrapper over `lab.py`. This becomes the shared structure every
subsequent Vertical Slice adds a sibling module to (`research_helper/search.py`,
`research_helper/papers.py`, …), per `tech-stack.md` Components.

## Complexity Tracking

*(no entries — no constitution violation introduced)*
