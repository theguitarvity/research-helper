# Feature Specification: Reference Resolution

**Feature dir**: `006-vs006-reference-resolution` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 6 (VS006); `fundactional.md` §8, §9 (Level 2), §35, §52

## User Scenarios & Testing

### User Story 1 - Resolve references against independent sources (P1)

**Acceptance Scenarios**:

1. **Given** normalized references with DOIs, **When** resolution runs
   and a source client returns an exact DOI match, **Then** the
   reference's state becomes `VERIFIED`.
2. **Given** a reference with no DOI, **When** resolution finds one
   sufficiently similar candidate by title, **Then** state becomes
   `RESOLVED`; if multiple similarly-strong candidates tie, state becomes
   `AMBIGUOUS`; if none are found, state becomes `UNAVAILABLE`.
3. **Given** every reference in a paper, **When** resolution completes,
   **Then** `references.bib` is emitted with only real, resolved fields —
   never fabricated ones.

### User Story 2 - Flag bibliographic inconsistencies (P1)

**Acceptance Scenarios**:

1. **Given** a citation whose in-text year (parsed from `raw_text`)
   differs from the resolved record's year, **When** resolution
   completes, **Then** the reference carries a `year_mismatch`
   consistency flag rather than silently adopting the resolved year as if
   it were what was cited.

### Edge Cases

- Never treat the citing paper's own text as sufficient evidence — every
  state above `DISCOVERED` requires having queried an independent
  external source (constitution Principle IV, §35).
- No candidate above the similarity threshold is `UNAVAILABLE`, never
  automatically `INVALID` — `INVALID`/`SUSPECTED_INVALID` require human
  review and are out of this slice's automatic scope.

## Requirements

### Functional Requirements

- **FR-001**: `resolve_reference` MUST query independent external sources
  (reusing the VS003 `SearchClient` protocol) for every reference — never
  infer existence from the citing text alone.
- **FR-002**: An exact DOI match against a source result MUST set state
  `VERIFIED`.
- **FR-003**: A title-similarity match above a fixed threshold (no DOI
  confirmation) MUST set state `RESOLVED`.
- **FR-004**: Multiple near-tied top candidates MUST set state
  `AMBIGUOUS`; zero candidates MUST set state `UNAVAILABLE`.
- **FR-005**: When a candidate is found, the in-text year (parsed from
  `raw_text` via a 19xx/20xx pattern) MUST be compared to the candidate's
  year; a mismatch MUST be recorded as a `year_mismatch` consistency flag
  on the resolved reference, never silently overwritten.
- **FR-006**: `resolve_references(paper_dir, clients)` MUST write
  `references.resolved.json` and `references.bib` (only fields backed by
  a resolved record; `UNAVAILABLE` entries emit a comment-only stub, no
  fabricated fields).
- **FR-007**: A client failure during resolution MUST NOT abort
  resolution of the remaining references (same failure-isolation
  requirement as VS003 search).

### Key Entities

- **ResolvedReference**: `raw_text, doi, title, authors, year, venue,
  url, source, state, consistency_flags`.

## Success Criteria

- **SC-001**: An exact-DOI fixture resolves to `VERIFIED`.
- **SC-002**: A no-match fixture resolves to `UNAVAILABLE`, never raises.
- **SC-003**: A year-mismatched fixture carries exactly one
  `year_mismatch` flag with both years recorded.
- **SC-004**: `references.bib` contains a valid BibTeX entry for every
  `VERIFIED`/`RESOLVED` reference and a clearly-marked stub for
  `UNAVAILABLE` ones.

## Assumptions

- `fundactional.md` §52's example output buckets ("verified / ambiguous /
  unavailable / unresolved") are mapped onto this slice's 4 reachable
  states as: `unresolved` ≈ `UNAVAILABLE` (no candidate found);
  `INVALID`/`SUSPECTED_INVALID` are not automatically reachable from this
  slice — they require the human-review path in VS009. *(INFERRED,
  explicitly flagged since §52 doesn't define its bucket names formally)*
- Title-similarity threshold (0.6, `difflib.SequenceMatcher` ratio) and
  "near-tied" margin (0.05) are implementation defaults, not sourced from
  the context files — tunable later without changing the public
  interface. *(INFERRED)*
