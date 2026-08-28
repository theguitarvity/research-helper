# Feature Specification: Experiment Scaffolder

**Feature dir**: `012-vs012-experiment-scaffolder` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 12 (VS012); `fundactional.md` §21-23

## User Scenarios & Testing

### User Story 1 - Scaffold a reproducible experiment (P1)

**Acceptance Scenarios**:

1. **Given** `research-helper experiment init attention-cache`, **When**
   it runs, **Then** the exact §21 structure is created
   (`README.md, hypothesis.md, protocol.md, environment/, src/, scripts/,
   datasets/, raw/, results/, analysis/, figures/, logs/, manifest.yaml`)
   with a schema-valid `manifest.yaml` per §22.
2. **Given** a reproduction command is supplied, **When** the manifest is
   written, **Then** `reproduction.command` is exactly that string, never
   altered or guessed.

### User Story 2 - LLM-involving experiments record extra fields (P2)

**Acceptance Scenarios**:

1. **Given** `provider`/`model`/etc. are supplied, **When** the manifest
   is written, **Then** an `llm` section records them; when not supplied,
   no `llm` section is fabricated.

## Requirements

### Functional Requirements

- **FR-001**: `init_experiment(paths, name, ...)` MUST create every §21
  directory/file, never fabricating a subdirectory not listed in §21.
- **FR-002**: The manifest MUST match §22's schema: `experiment (id,
  title, created_at, status)`, `research_question`, `hypothesis`,
  `variables (independent, dependent, controlled)`, `dataset`,
  `environment`, `reproduction.command`, `outputs`.
- **FR-003**: `id` MUST be sequential `EXP-NNN`, derived by scanning
  existing `experiments/*/manifest.yaml` (never reused).
- **FR-004**: When LLM-related parameters are supplied, an `llm` section
  (`provider, model, temperature, system_prompt, input_artifact,
  output_artifact`) MUST be added; when none are supplied, no `llm`
  section is written (never a section of nulls).
- **FR-005**: Re-running `init_experiment` for a name that already has a
  `manifest.yaml` MUST NOT overwrite it (idempotent, consistent with
  VS001/VS004's convention).

## Success Criteria

- **SC-001**: A fresh experiment has exactly the §21 structure — no more,
  no less.
- **SC-002**: `manifest.yaml` round-trips (parses back to the exact
  values passed in).
- **SC-003**: An experiment created without LLM parameters has no `llm`
  key in its manifest at all.

## Assumptions

None beyond §21-23's schema, which is explicit.
