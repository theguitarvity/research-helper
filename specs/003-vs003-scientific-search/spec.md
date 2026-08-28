# Feature Specification: Scientific Search

**Feature dir**: `003-vs003-scientific-search` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 3 (VS003); `fundactional.md` §7, §38

## User Scenarios & Testing

### User Story 1 - Structured multi-source search (P1)

A researcher searches for literature by topic/date range and gets a
deduplicated, schema-normalized result set, without having to know each
API's response shape.

**Independent Test**: inject fake `SearchClient` implementations returning
overlapping fixture results; call `run_search`; assert normalized, deduped
output.

**Acceptance Scenarios**:

1. **Given** two sources return the same paper (same DOI), **When**
   `run_search` merges results, **Then** only one `SearchResult` for that
   DOI survives, and both sources are noted for auditability.
2. **Given** a query with `from`/`to` years, **When** results are
   returned, **Then** every result's `year` (if known) is inside the
   requested range.

---

### User Story 2 - Reproducible search manifest (P1)

Every executed search leaves a manifest so it can be re-run or audited
later without re-asking the researcher what was searched.

**Independent Test**: run a search, assert
`literature/searches/<date>-<slug>/{query.yaml,raw-results.json,
normalized.json,selected.json,README.md}` all exist and `query.yaml`
round-trips the original parameters.

**Acceptance Scenarios**:

1. **Given** a completed search, **When** its `query.yaml` is read back,
   **Then** it contains the exact query/sources/filters/`executed_at`
   used.

### Edge Cases

- A source client raises (network error / bad response): that source's
  results are dropped and recorded as failed in the manifest's `README.md`
  rather than aborting the whole search — partial results still count as
  a completed search.
- No client returns any result: `run_search` returns an empty list and
  still writes a (empty-result) manifest, never silently skips persisting.

## Requirements

### Functional Requirements

- **FR-001**: `SearchResult` MUST have `title, authors, year, doi, venue,
  abstract, url, pdf_url, open_access, source` per the schema in
  `fundactional.md` §7.
- **FR-002**: A `SearchClient` Protocol MUST exist so any source
  (Semantic Scholar, Crossref, OpenAlex, or a test double) can be passed
  to `run_search` interchangeably.
- **FR-003**: Deduplication priority MUST be DOI, then normalized title,
  then authors+year, in that order — never merge two results that don't
  match on at least one of these.
- **FR-004**: `run_search` MUST write a search manifest under
  `literature/searches/<YYYY-MM-DD>-<slug>/` with `query.yaml`,
  `raw-results.json` (pre-dedup, per source), `normalized.json`
  (post-dedup), `selected.json` (defaults to the full normalized set,
  overridable), and `README.md`.
- **FR-005**: A client failure MUST NOT abort the whole search; it MUST
  be recorded, and the search MUST still complete with whatever other
  sources returned.
- **FR-006**: Real API clients (Semantic Scholar, Crossref, OpenAlex)
  MUST be implemented against `httpx`, injectable/mockable, with no
  business logic (dedup, manifest writing) inside a client itself.

### Key Entities

- **SearchResult**: one normalized bibliographic record.
- **SearchQuery**: query string, date range, languages, max_results,
  sources.
- **Search Manifest**: the persisted, reproducible record of one search.

## Success Criteria

- **SC-001**: Duplicate DOIs across two fake sources collapse to one
  result in `normalized.json`.
- **SC-002**: 100% of searches (including zero-result and partial-failure
  ones) produce a complete manifest directory.
- **SC-003**: Re-running the exact parameters from a saved `query.yaml`
  reproduces the same `SearchQuery` object (round-trip, not necessarily
  the same live results).

## Assumptions

- Live API field mappings for Semantic Scholar/Crossref/OpenAlex are
  implemented per each API's public documentation but are **not
  live-verified** in this offline environment; they are covered by tests
  using realistic fixture payloads shaped like each API's documented
  response, injected via a mocked `httpx` transport (`respx`). This is
  recorded as a known limitation, not silently claimed as live-tested.
  *(INFERRED, flagged per protocol's honesty requirement)*
