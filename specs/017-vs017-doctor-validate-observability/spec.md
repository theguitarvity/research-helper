# Feature Specification: Doctor / Validation / Observability

**Feature dir**: `017-vs017-doctor-validate-observability` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 17 (VS017); `fundactional.md` §40, §48,
§63; `globalization.md` §61.3, §62, §64

## User Scenarios & Testing

### User Story 1 - Environment doctor (P1)

**Acceptance Scenarios**:

1. **Given** this machine (macOS), **When** `research-helper doctor`
   runs, **Then** it reports OS/arch/shell plus Python/uv/git/LaTeX/
   BibTeX/agent detection in the §63 shape, using real `shutil.which`/
   `platform` calls — never a guessed or hardcoded result.

### User Story 2 - Structural validation across every artifact type (P1)

**Acceptance Scenarios**:

1. **Given** a lab with one broken fixture per gate (bad reference
   schema, missing provenance, duplicate DOI, a wikilink to a
   non-existent note, unbalanced BibTeX braces, a `\input` to a missing
   LaTeX section, an experiment with no manifest, a corrupt
   `handoff.json`), **When** `research-helper validate` runs, **Then**
   every one of those is reported as a distinct issue and the command
   exits non-zero.
2. **Given** a clean lab, **When** `validate` runs, **Then** it reports
   zero issues and exits 0.

### User Story 3 - Observability without secrets (P1)

**Acceptance Scenarios**:

1. **Given** a logged event, **When** `log_event` is called, **Then**
   only the fixed §40 field set (`task, agent, tool, duration, cache_hit,
   tokens, status, artifacts`) can be written — there is no parameter
   through which an arbitrary (and therefore possibly secret-bearing)
   key could reach the log line.

### User Story 4 - Global config path resolution (P2)

**Acceptance Scenarios**:

1. **Given** an injected platform name (`Windows`/`Darwin`/`Linux`),
   **When** `global_config_dir(system=...)` is called, **Then** it
   returns the §64 convention for that OS — verified for all three via
   injection, live-verified only for macOS (this environment).

## Requirements

### Functional Requirements

- **FR-001**: `doctor(paths=None)` MUST report platform (OS, arch,
  shell), core tools (python, uv, git), research tools (PDF extractor
  i.e. pypdf import check), academic tools (latexmk, bibtex), and agent
  adapters found (`.claude`, `.codex`, `.github`, `.gemini` presence),
  all via real detection calls.
- **FR-002**: `validate(paths)` MUST run all ten §48 gate checks (schema
  validity, manifest validity, broken wiki links, duplicate DOI, missing
  provenance, missing hashes, invalid BibTeX, broken LaTeX, missing
  experiment metadata, invalid handoff) and return one `ValidationIssue`
  per problem found — never silently skip a gate.
- **FR-003**: The broken-wiki-link gate MUST resolve `[[links]]` against
  the same title mapping `research_helper.vault.sync_vault` uses (via
  `research_helper.graph.build_graph`), not just filenames, so it never
  false-positives on the vault's own title-based linking convention.
- **FR-004**: `log_event(paths, *, task=None, agent=None, tool=None,
  duration=None, cache_hit=None, tokens=None, status=None,
  artifacts=None)` MUST be the only way to append to
  `logs/research-helper.jsonl`, with no `**kwargs` passthrough that could
  smuggle an arbitrary (secret-shaped) key into a log line.
- **FR-005**: `global_config_dir(system=None)` MUST implement the §64
  mapping (`Windows→%APPDATA%\research-helper`, `Darwin→~/Library/
  Application Support/research-helper`, else→`$XDG_CONFIG_HOME or
  ~/.config/research-helper`), accepting an injectable `system` string
  for testing all three branches without mocking global interpreter
  state.
- **FR-006**: `scripts/bootstrap.py` MUST hold the real cross-platform
  detection logic; `scripts/bootstrap.sh`/`scripts/bootstrap.ps1` MUST be
  thin wrappers that only invoke it (§78 "One Core" principle, no logic
  duplicated per OS).

## Success Criteria

- **SC-001**: `doctor()` run on this machine reports `Python: OK`,
  `git: OK` (both installed here) without hardcoding.
- **SC-002**: A lab with one deliberately broken fixture per gate
  produces exactly one issue per gate (10 total) and a clean lab produces
  zero.
- **SC-003**: `log_event`'s signature has no way to pass an arbitrary key
  — attempting `log_event(paths, api_key="x")` raises `TypeError`.
- **SC-004**: `global_config_dir("Windows")`, `global_config_dir("Darwin")`,
  and `global_config_dir("Linux")` each match §64 exactly.

## Assumptions

- Windows/Linux/Termux `global_config_dir` branches are verified by
  parameter injection in this environment (macOS), not by running on
  those OSes — recorded as a known limitation per the protocol's honesty
  requirement, not silently claimed as live-tested. *(EXPLICIT, per
  `app-features.md` VS017 acceptance criteria)*
