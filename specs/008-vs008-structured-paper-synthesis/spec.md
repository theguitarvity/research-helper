# Feature Specification: Structured Paper Synthesis

**Feature dir**: `008-vs008-structured-paper-synthesis` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 8 (VS008); `fundactional.md` §11

## Architecture note (read before Requirements)

Producing the actual prose for each synthesis section (what the paper's
research problem *is*, what its contributions *are*, …) is judgment/
reasoning work, not a deterministic operation — constitution Principle
III assigns that to the agent, not to a script. This module is therefore
the **deterministic scaffolding and persistence layer**: it defines the
exact §11 schema, renders it to Markdown (with "Not defined by current
context." for anything left unset — never fabricated filler), and writes
it to the right path. The agent computes section content (by reading the
paper) and passes it in; this module never reads a PDF or calls an LLM
itself. *(INFERRED architecture decision, recorded because it isn't
spelled out verbatim in the context files)*

## User Scenarios & Testing

### User Story 1 - Persist a structured per-paper synthesis (P1)

**Acceptance Scenarios**:

1. **Given** a `PaperSynthesis` with some sections filled in and others
   left unset, **When** it's written, **Then** the output file has every
   §11 section heading, filled sections show their content verbatim, and
   unset sections show exactly "Not defined by current context." —
   never invented text.

### User Story 2 - Cross-paper comparative synthesis (P2)

**Acceptance Scenarios**:

1. **Given** comparative content for some or all of the four cross-paper
   artifacts, **When** `write_comparative_synthesis` runs, **Then** all
   four files (`comparison.md`, `disagreements.md`,
   `common-findings.md`, `research-gaps.md`) exist, each either with the
   given content or the same not-defined fallback.

## Requirements

### Functional Requirements

- **FR-001**: `PaperSynthesis` MUST have one optional string field per
  §11 section, in §11's order.
- **FR-002**: `render_synthesis` MUST render every field as its own `##`
  heading in §11's order, using "Not defined by current context." for any
  unset field.
- **FR-003**: `write_individual_synthesis(paths, paper_id, synthesis)`
  MUST write to `literature/synthesis/individual/<paper_id>.md`.
- **FR-004**: `write_comparative_synthesis(paths, **sections)` MUST
  always write all four cross-paper files, using the same not-defined
  fallback for any omitted section.
- **FR-005**: Neither function may read a PDF, call an LLM, or fabricate
  section content — inputs are taken as given.

## Success Criteria

- **SC-001**: A synthesis with 3 of 17 sections filled renders exactly 3
  real sections and 14 "Not defined by current context." sections, in
  the correct order.
- **SC-002**: `write_comparative_synthesis()` called with zero arguments
  still produces all four files.

## Assumptions

- CLI surface: `research-helper summarize <paper> --from-json
  <sections.json>` reads agent-computed section content from a JSON file
  rather than generating it — consistent with the architecture note
  above. *(INFERRED)*
