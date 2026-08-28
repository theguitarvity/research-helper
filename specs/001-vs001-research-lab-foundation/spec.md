# Feature Specification: Research Lab Foundation

**Feature Branch**: `001-vs001-research-lab-foundation` (trunk workflow — no branch created; directory-scoped)

**Created**: 2026-08-27

**Status**: Draft

**Input**: `.spec-master/context/app-features.md` Feature 1 (VS001), `fundactional.md` §24, §67-70, `globalization.md` §61.1, §68-69

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initialize a new Research Lab (Priority: P1)

A researcher runs `research-helper init` in an empty directory and gets a
complete, working Research Lab layout, ready for every later Vertical
Slice to write into.

**Why this priority**: every other Vertical Slice depends on this
structure existing; it is the literal foundation.

**Independent Test**: run `research-helper init` in a temp directory and
assert every canonical subdirectory and `research-helper.yaml` exist.

**Acceptance Scenarios**:

1. **Given** an empty directory, **When** `research-helper init` runs,
   **Then** `.agent/`, `research/memory/`, `library/`, `literature/`,
   `experiments/`, `papers/`, `graph/`, `vault/`, `logs/`, and
   `research-helper.yaml` are created.
2. **Given** `.agent/` was created, **When** its contents are inspected,
   **Then** it contains `agents/research-helper/`, `skills/`, `scripts/`,
   `schemas/`, `templates/`, `state/`, `adapters/`.

---

### User Story 2 - Re-run init without losing work (Priority: P1)

A researcher re-runs `research-helper init` on a lab that already has
research in it (papers imported, notes written) and nothing is
overwritten or deleted.

**Why this priority**: idempotency is an explicit acceptance criterion
(`app-features.md` VS001) — a destructive re-init would violate the
"researcher control" success priority (§60).

**Independent Test**: init, create a marker file inside `library/papers/`,
init again, assert the marker file is untouched.

**Acceptance Scenarios**:

1. **Given** an already-initialized lab with existing content, **When**
   `research-helper init` runs again, **Then** exit code is 0, no existing
   file is modified or deleted, and any missing canonical subdirectory is
   created.

---

### User Story 3 - Initialize at an explicit path (Priority: P2)

A researcher runs `research-helper init ~/research/agentic-se` from
anywhere and a lab is created at that path, not at the current directory.

**Why this priority**: explicit-path init is EXPLICIT in `fundactional.md`
§67 but is not required for the single-directory MVP smoke test, hence P2.

**Independent Test**: run `research-helper init <tmp>/nested/newdir` from
an unrelated cwd; assert the lab exists at the target and parent
directories were created.

**Acceptance Scenarios**:

1. **Given** a path that doesn't exist yet, **When**
   `research-helper init <path>` runs, **Then** all parent directories are
   created and the lab is scaffolded at `<path>`, not at `cwd`.

### Edge Cases

- Running `init` inside a directory that is itself nested under an
  existing Research Lab: per the workspace-resolution priority (Current
  Directory → Nearest Research Lab Root → User Global Configuration,
  `globalization.md` §61.1), `init <no-path>` targets the **current**
  directory, not the ancestor lab — resolution priority governs *finding*
  a lab for other commands, not where `init` writes.
- A path segment containing characters invalid on another OS (e.g. `:` on
  Windows) is out of scope for the MVP: `init` uses the path exactly as
  given and lets the OS filesystem call fail naturally, no lookahead
  path-sanitization is added (`NEEDS CLARIFICATION` avoided: nothing in
  the context files requires cross-OS path sanitization, only
  workspace-relative *storage* of paths — §69 is about not persisting
  absolute paths in data, not about sanitizing user-supplied CLI targets).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST provide `research-helper init [PATH]`, defaulting
  `PATH` to the current working directory.
- **FR-002**: `init` MUST create, if missing: `.agent/agents/research-helper/`,
  `.agent/skills/`, `.agent/scripts/`, `.agent/schemas/`, `.agent/templates/`,
  `.agent/state/`, `.agent/adapters/`, `research/memory/`, `library/papers/`,
  `library/books/`, `library/articles/`, `library/datasets/`,
  `literature/searches/`, `literature/references/`, `literature/synthesis/`,
  `experiments/`, `papers/`, `graph/`, `vault/`, `logs/`, and
  `research-helper.yaml`.
- **FR-003**: `init` MUST be idempotent: re-running it on an already
  initialized (or partially initialized) lab MUST NOT modify or delete any
  existing file, and MUST create only what's missing.
- **FR-004**: `init` MUST accept an explicit target path and create any
  missing parent directories.
- **FR-005**: All path values written into `research-helper.yaml` or any
  other lab manifest MUST be workspace-relative; the core MUST use
  `pathlib.Path` exclusively for path construction/joining (never manual
  string concatenation of path separators).
- **FR-006**: The lab-root resolver MUST implement the priority order:
  current directory → nearest ancestor Research Lab root (a directory
  containing `research-helper.yaml`) → user global configuration path.
- **FR-007**: `research-helper.yaml` MUST record, at minimum, the schema/
  tool version that created the lab (feeds VS017's `generated_by`
  convention) and the workflow default (search sources, venue) as
  placeholders/defaults for now — no other Vertical Slice's fields are
  invented here.

### Key Entities

- **Research Lab**: the root directory identified by
  `research-helper.yaml`; owns every canonical subdirectory below it.
- **Lab Paths**: a typed accessor object exposing every canonical
  directory as a `pathlib.Path` relative to the resolved lab root — every
  other Vertical Slice's module resolves paths through this, never by
  reconstructing segments itself (constitution Principle VII).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `research-helper init` on an empty directory exits 0 and
  creates 100% of the canonical structure in FR-002 in a single run.
- **SC-002**: Running `init` twice in a row produces zero filesystem diffs
  on the second run beyond creating anything that was still missing.
- **SC-003**: Zero absolute or backslash-containing path strings appear in
  any file `init` writes (verified by a test asserting on the literal
  written content, not just behavior).

## Assumptions

- The lab-root marker file is `research-helper.yaml` (not, e.g., a hidden
  dotfile) — chosen because §67 explicitly names it as an `init` output;
  using it as the marker avoids inventing a second file. *(INFERRED)*
- `.agent/skills/`, `.agent/schemas/`, `.agent/templates/` start empty in
  VS001 and are populated by later slices (VS003+ each contribute their
  own skill folder) — VS001 only guarantees the directories exist.
  *(INFERRED from dependency order in `app-features.md`)*
