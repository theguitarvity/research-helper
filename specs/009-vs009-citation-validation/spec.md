# Feature Specification: Citation Validation

**Feature dir**: `009-vs009-citation-validation` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 9 (VS009); `fundactional.md` §9, §35, §36

## Architecture note

Level 1 (Existence) and Level 2 (Bibliographic Consistency) are fully
derivable from VS006's `ResolvedReference` (its `state` and
`consistency_flags`) — deterministic, computed here. Level 3 (Claim
Support) requires reading and comparing meaning between a claim and the
cited paper — reasoning work for the agent (constitution Principle III,
same boundary as VS008); this module validates and persists the agent's
Level-3 classification, it does not compute it.

## User Scenarios & Testing

### User Story 1 - Three-level validation record (P1)

**Acceptance Scenarios**:

1. **Given** a `VERIFIED` resolved reference, **When** validated,
   **Then** `existence_state == "VERIFIED"`.
2. **Given** an `UNAVAILABLE`/`AMBIGUOUS` resolved reference, **When**
   validated, **Then** `existence_state == "UNVERIFIED"` — never
   `SUSPECTED_INVALID` automatically.
3. **Given** a resolved reference carrying a `year_mismatch` consistency
   flag, **When** validated, **Then** that flag is carried into the
   validation record unchanged.
4. **Given** agent-supplied claim-support evidence/justification/
   confidence, **When** validated, **Then** they are persisted verbatim,
   with `claim_support` restricted to the five allowed values.

### User Story 2 - UNVERIFIED must precede SUSPECTED_INVALID (P1)

**Acceptance Scenarios**:

1. **Given** a validation whose `existence_state` is anything other than
   `UNVERIFIED`, **When** `mark_suspected_invalid` is called, **Then** it
   raises rather than silently escalating.
2. **Given** an `UNVERIFIED` validation, **When**
   `mark_suspected_invalid` is called, **Then** `existence_state`
   becomes `SUSPECTED_INVALID`.

## Requirements

### Functional Requirements

- **FR-001**: `CitationValidation` MUST have `existence_state` ∈
  `{VERIFIED, RESOLVED, UNVERIFIED, SUSPECTED_INVALID}`,
  `consistency_flags: list[str]`, `claim_support` ∈ `{SUPPORTED,
  PARTIALLY_SUPPORTED, NOT_SUPPORTED, CONTRADICTED, UNCLEAR, None}`,
  `evidence`, `justification`, `confidence` (0.0-1.0).
- **FR-002**: `validate_citation` MUST derive `existence_state` from the
  resolved reference's `state` (`VERIFIED`→`VERIFIED`,
  `RESOLVED`→`RESOLVED`, anything else→`UNVERIFIED`) — never
  `SUSPECTED_INVALID` from this path.
- **FR-003**: `validate_citation` MUST copy `consistency_flags` from the
  resolved reference verbatim.
- **FR-004**: `mark_suspected_invalid(validation)` MUST raise `ValueError`
  unless `existence_state == "UNVERIFIED"`.
- **FR-005**: `confidence`, when given, MUST be constrained to `[0.0,
  1.0]` (schema-enforced, not merely documented).
- **FR-006**: `validate_citations(paper_dir, resolved_refs, claims=None)`
  MUST write `citations.json` into the paper's directory.

## Success Criteria

- **SC-001**: Every resolution state maps to the correct
  `existence_state` per FR-002.
- **SC-002**: `mark_suspected_invalid` on a non-`UNVERIFIED` validation
  raises; on `UNVERIFIED` it succeeds.
- **SC-003**: An out-of-range confidence value is rejected at
  construction time.

## Assumptions

None beyond the Architecture note above.
