# Feature Specification: Paper Import

**Feature dir**: `004-vs004-paper-import` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 4 (VS004); `fundactional.md` §25, §26

## User Scenarios & Testing

### User Story 1 - Import a paper with a known DOI (P1)

A researcher imports a PDF whose DOI is known; it lands under a stable,
DOI-derived identifier with provenance recorded.

**Acceptance Scenarios**:

1. **Given** a PDF and its DOI, **When** `import_paper` runs, **Then**
   `library/papers/<doi-with-slashes-as-underscores>/paper.pdf` exists and
   `manifest.json` records `sha256`, `doi`, `retrieved_at`, `source`,
   `license`, `open_access`.

### User Story 2 - Import a paper without a DOI (P1)

A researcher imports a PDF with no known DOI; a stable hash-based
identifier is used instead, never blocking the import.

**Acceptance Scenarios**:

1. **Given** a PDF with no DOI, **When** `import_paper` runs, **Then** it
   is stored under `library/papers/paper-<hash-prefix>/` with the same
   provenance fields (`doi: null`).

### User Story 3 - Re-import is not destructive or duplicated (P2)

**Acceptance Scenarios**:

1. **Given** a paper already imported, **When** the same file is imported
   again, **Then** no second copy is created and the existing
   `manifest.json` is left untouched (idempotent).

### Edge Cases

- Two different files happen to share a DOI (shouldn't normally happen,
  but not this slice's job to adjudicate): the second import overwrites
  neither `paper.pdf` nor `manifest.json` of the first — it is treated as
  "already imported" by identifier, and a warning is surfaced to the
  caller rather than silently merging content. *(INFERRED — no explicit
  requirement covers this collision case)*

## Requirements

### Functional Requirements

- **FR-001**: `import_paper(paths, file_path, *, doi=None, source=None,
  original_url=None, license=None, open_access=False)` MUST compute the
  file's `sha256` and use it as the fallback identifier basis.
- **FR-002**: Identifier MUST be `doi.replace("/", "_")` when a DOI is
  given, else `paper-{sha256[:16]}` (§25).
- **FR-003**: MUST create `library/papers/<identifier>/paper.pdf` (copy,
  never move/delete the source file) and `manifest.json` with the
  provenance schema from §26 (`source, original_url, doi, retrieved_at,
  sha256, license, open_access`).
- **FR-004**: MUST create a `metadata.json` stub (`doi`, `title: null`)
  when absent — title is populated by later slices (synthesis/search),
  never fabricated here.
- **FR-005**: Re-importing into an identifier directory that already has
  a `paper.pdf` and `manifest.json` MUST NOT overwrite either file.

### Key Entities

- **Provenance**: per §26 schema, attached to every acquired document.

## Success Criteria

- **SC-001**: Importing a DOI'd fixture PDF twice results in exactly one
  `paper.pdf` on disk and one, unmodified `manifest.json`.
- **SC-002**: Importing a no-DOI fixture PDF never raises and produces a
  hash-based identifier directory.

## Assumptions

- "Legally supplied by the researcher" import (this command) always sets
  `source="researcher-supplied"` unless a different source is passed —
  VS007 (Open Access Acquisition) is what sets `source` to
  `crossref`/`openalex`/etc. for machine-discovered downloads.
  *(INFERRED)*
