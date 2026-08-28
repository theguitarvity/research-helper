# Feature Specification: Reference Extraction

**Feature dir**: `005-vs005-reference-extraction` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 5 (VS005); `fundactional.md` §8, §52

## User Scenarios & Testing

### User Story 1 - Extract references from an imported paper (P1)

**Acceptance Scenarios**:

1. **Given** an imported paper with a detectable references section,
   **When** `research-helper references extract <paper>` runs, **Then**
   it reports "N references discovered" and writes
   `references.raw.json` + `references.normalized.json` into the paper's
   directory.
2. **Given** a PDF with no detectable references section, **When**
   extraction runs, **Then** it reports 0 discovered and does not raise.

### Edge Cases

- A reference string containing an embedded DOI MUST have that DOI
  opportunistically captured at extraction time (helps VS006 resolve
  faster) — this is a convenience field, not a resolution.

## Requirements

### Functional Requirements

- **FR-001**: Extraction MUST use a real text-extraction library
  (`pypdf`) rather than a hand-rolled binary PDF parser (§42).
- **FR-002**: A `RawReference` (`raw_text`, `doi`, `state="DISCOVERED"`)
  MUST be produced per detected reference entry.
- **FR-003**: Reference-section detection MUST look for a
  `References`/`Bibliography` heading line; absence of such a heading
  MUST yield zero references, not an exception.
- **FR-004**: Splitting MUST support bracket-numbered (`[1] ...`) and
  plain-numbered (`1. ...`) reference lists; if neither pattern matches,
  fall back to paragraph (blank-line) splitting.
- **FR-005**: `extract_references` MUST be deterministic (no LLM call)
  and MUST write both `references.raw.json` (as detected) and
  `references.normalized.json` (whitespace-normalized, exact-duplicate
  entries removed).
- **FR-006**: A DOI appearing inside a reference string MUST be captured
  into that reference's `doi` field via pattern matching
  (`10.\d{4,9}/...`).

## Success Criteria

- **SC-001**: A fixture PDF with N bracket-numbered references yields
  exactly N `RawReference` entries.
- **SC-002**: A fixture PDF with no references section yields 0 entries
  and no exception.
- **SC-003**: A reference string with an embedded DOI has that DOI
  captured verbatim (case/format preserved).

## Assumptions

- No GROBID dependency (offline-first, `globalization.md` §73) — the
  heuristic splitter is the MVP default; a future ADR may add GROBID as
  an optional, `doctor`-detected enhancement. *(from `tech-stack.md`,
  already recorded there — restated here as this slice's actual pin)*
