# Feature Specification: Obsidian Research Memory

**Feature dir**: `011-vs011-obsidian-research-memory` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 11 (VS011); `fundactional.md` §14-15

## User Scenarios & Testing

### User Story 1 - Sync a script-generated Obsidian vault (P1)

**Acceptance Scenarios**:

1. **Given** imported papers with a built citation graph, **When**
   `sync_vault` runs, **Then** every imported paper gets a
   `vault/Papers/<id>.md` note with frontmatter and a `## References`
   section linking only to papers actually present as vault notes
   (`[[wikilink]]`) — an external (non-imported) cited record is listed
   by title/DOI as plain text, never as a broken wikilink.
2. **Given** the same library and graph, **When** `sync_vault` runs
   twice, **Then** the output is byte-identical (idempotent, no manual
   link-editing).

### User Story 2 - Compact context checkpoint (P1)

**Acceptance Scenarios**:

1. **Given** an active Research Task, **When**
   `write_current_context` runs, **Then**
   `research/memory/current-context.md` has one section per §15 bullet
   (research being done, problem, hypotheses, important papers, active
   experiments, open questions, next steps) — each either populated from
   real data or explicitly "Not defined by current context."

## Requirements

### Functional Requirements

- **FR-001**: `sync_vault(paths)` MUST derive every paper note and every
  reference link from `build_graph` (VS010) output — never write a link
  the graph doesn't support.
- **FR-002**: A `CITES` edge to another *imported* paper MUST render as
  `[[title-or-id]]`; a `CITES` edge to an external (non-imported) node
  MUST render as plain text, never a wikilink to a note that doesn't
  exist.
- **FR-003**: Each paper note's `## Summary` MUST come from
  `literature/synthesis/individual/<id>.md` when present, else the
  standard not-defined marker — never fabricated.
- **FR-004**: `sync_vault` MUST be idempotent given unchanged source
  data.
- **FR-005**: `write_current_context(paths)` MUST produce one section per
  §15 bullet, sourced from the active `ResearchTask` (VS002) and the
  imported-papers list where available, and the not-defined marker where
  no slice yet models the data (hypotheses, active experiments, open
  questions — none of VS002-VS010 model these fields yet).

## Success Criteria

- **SC-001**: A 2-paper library where A cites B (both imported) produces
  a `[[B's title]]` wikilink inside A's note.
- **SC-002**: A citation to a non-imported record renders as plain text
  in A's note, not `[[...]]`.
- **SC-003**: Two consecutive `sync_vault` calls produce byte-identical
  files.
- **SC-004**: `current-context.md` contains all 7 section headings from
  §15.

## Assumptions

- `ResearchTask` doesn't yet distinguish "what research is being done"
  from "what problem is being investigated" — both render the task's
  `objective` field. This is a known MVP data-model gap, not a bug; a
  future slice may split them. *(INFERRED, explicitly flagged)*
