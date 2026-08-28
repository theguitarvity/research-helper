# Tasks: Research Lab Foundation

**Input**: `plan.md`, `spec.md` in this directory

## Phase 1 — Project bootstrap (shared, not story-specific)

- [ ] T001 Create `pyproject.toml` (uv-managed, Python >=3.12, deps: typer,
      pydantic, pyyaml, httpx; dev deps: pytest, ruff, mypy)
- [ ] T002 Create `research_helper/__init__.py` with `__version__`
- [ ] T003 [P] Create `tests/conftest.py` with a `lab_dir` fixture
      (`tmp_path`)

## Phase 2 — User Story 1: Initialize a new Research Lab (P1)

- [ ] T010 [US1] `research_helper/lab.py`: `LAB_SUBDIRS` constant listing
      every FR-002 directory as relative `Path` segments
- [ ] T011 [US1] `research_helper/lab.py`: `scaffold(root: Path) -> None`
      creates every missing subdir + `research-helper.yaml` if absent
- [ ] T012 [US1] `research_helper/cli.py`: Typer app + `init` command
      calling `scaffold(Path(path or "."))`
- [ ] T013 [US1] `tests/test_lab.py::test_scaffold_creates_all_dirs`

## Phase 3 — User Story 2: Idempotent re-run (P1)

- [ ] T020 [US2] `tests/test_lab.py::test_scaffold_idempotent_preserves_content`
      — write a marker file, re-run `scaffold`, assert marker untouched and
      mtimes of pre-existing files unchanged
- [ ] T021 [US2] `research_helper/lab.py`: ensure `scaffold` never truncates
      an existing `research-helper.yaml` (write only if absent)

## Phase 4 — User Story 3: Explicit path init (P2)

- [ ] T030 [US3] `tests/test_cli_init.py::test_init_explicit_nested_path`
      — run `init` with a path several levels deep that doesn't exist yet
- [ ] T031 [US3] `research_helper/lab.py`: `scaffold` creates parent dirs
      (`Path.mkdir(parents=True, exist_ok=True)`)

## Phase 5 — Cross-cutting (SC-003, portability)

- [ ] T040 `research_helper/lab.py`: `resolve_lab_root(start: Path) -> Path
      | None` implementing current-dir → nearest-ancestor-with-manifest
      resolution (global-config fallback stubbed as `None` here; VS017
      implements the actual global-config read)
- [ ] T041 `tests/test_lab.py::test_no_absolute_or_backslash_paths_persisted`
      — read back `research-helper.yaml` as text, assert no absolute path
      and no `\` appears
- [ ] T042 `research_helper/lab.py`: `LabPaths` dataclass exposing every
      canonical directory as a typed `Path` property, used by CLI and
      (going forward) every later slice

## Dependencies

Phase 1 → Phase 2 → {Phase 3, Phase 4} → Phase 5. Each user story's tests
(T013, T020-021, T030-031) are independently runnable once Phase 2 lands.
