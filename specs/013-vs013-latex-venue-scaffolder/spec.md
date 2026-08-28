# Feature Specification: LaTeX / Venue Scaffolder

**Feature dir**: `013-vs013-latex-venue-scaffolder` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 13 (VS013); `fundactional.md` §19-20

## User Scenarios & Testing

### User Story 1 - Scaffold against the bundled generic venue (P1)

**Acceptance Scenarios**:

1. **Given** `research-helper paper init --venue generic --name x`,
   **When** it runs (fresh lab, no `venues/generic.yaml` registered
   yet), **Then** the §19 structure is created using the tool's built-in
   generic venue (no formatting requirements fabricated — the built-in
   generic venue's `requirements` are empty and its `assumptions` say so
   explicitly).

### User Story 2 - Unregistered venue fails clearly (P1)

**Acceptance Scenarios**:

1. **Given** `--venue wop` with no `venues/wop.yaml` present, **When**
   `paper init` runs, **Then** it raises a clear error naming the
   expected file path — it never invents WOP's actual requirements.

### User Story 3 - Registered venue is used and pinned (P2)

**Acceptance Scenarios**:

1. **Given** a researcher-authored `venues/acm.yaml` with real
   `requirements`, **When** `paper init --venue acm` runs, **Then**
   `papers/<name>/venue.json` pins the exact venue data used at that
   time (future registry updates don't silently alter the project, §76).

## Requirements

### Functional Requirements

- **FR-001**: `init_paper_project(paths, *, venue, name)` MUST create the
  exact §19 structure (`main.tex, references.bib,
  sections/{introduction,background,methodology,results,discussion,
  conclusion}.tex, figures/, tables/, assets/, Makefile, README.md`).
- **FR-002**: `load_venue(paths, venue_name)` MUST read
  `venues/<venue_name>.yaml` when present; for exactly `"generic"` with
  no such file, MUST fall back to a built-in venue with empty
  `requirements` and an explicit assumption disclaimer; for any other
  unregistered name, MUST raise `FileNotFoundError` naming the expected
  path — never fabricate real venue requirements.
- **FR-003**: The venue schema (`name, template_source,
  template_version, requirements, assumptions`) MUST keep `requirements`
  (externally verified) and `assumptions` (agent/tool assumptions)
  structurally separate (§20, explicit).
- **FR-004**: `papers/<name>/venue.json` MUST be a pinned snapshot of the
  venue data used at scaffold time.
- **FR-005**: Re-running `init_paper_project` for an existing project
  (an existing `main.tex`) MUST NOT overwrite it (idempotent).

## Success Criteria

- **SC-001**: `--venue generic` succeeds on a fresh lab with no
  registered venues.
- **SC-002**: `--venue wop` with nothing registered raises, and the
  error message names `venues/wop.yaml`.
- **SC-003**: A registered venue's `requirements` values appear verbatim
  in the generated `venue.json` — never altered.

## Assumptions

- `venues_dir` (`paths.venues_dir` → `<lab-root>/venues`) is a new
  `LabPaths` property, added here rather than retrofitting VS001's
  `LAB_SUBDIRS` — it's created on demand by this slice's `load_venue`/
  registration flow, not by `research-helper init` (venues are optional
  and lab-specific, unlike the always-present canonical directories).
  *(INFERRED)*
