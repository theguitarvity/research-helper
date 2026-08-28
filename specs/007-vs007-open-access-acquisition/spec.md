# Feature Specification: Open Access Acquisition

**Feature dir**: `007-vs007-open-access-acquisition` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 7 (VS007); `fundactional.md` §27-28

## User Scenarios & Testing

### User Story 1 - Download only what's legally available (P1)

**Acceptance Scenarios**:

1. **Given** a resolved reference with a known open-access PDF URL,
   **When** acquisition runs, **Then** the PDF is downloaded and the
   reference's `acquisition_state` becomes `DOWNLOADED`.
2. **Given** a resolved reference confirmed to exist but with no
   open-access URL, **When** acquisition runs, **Then**
   `acquisition_state` becomes `PAYWALLED` and no download is attempted.
3. **Given** a reference that couldn't be resolved to a specific record
   (`AMBIGUOUS`/`UNAVAILABLE`), **When** acquisition runs, **Then**
   `acquisition_state` becomes `METADATA_ONLY` — it is never dropped from
   the resolved set.

### User Story 2 - Cache avoids redundant downloads (P1)

**Acceptance Scenarios**:

1. **Given** a reference already downloaded once, **When** acquisition
   runs again for the same URL, **Then** the downloader is not called a
   second time (cache hit) and the same local file is reused.

## Requirements

### Functional Requirements

- **FR-001**: `ResolvedReference` MUST gain `pdf_url`, `open_access`
  (carried from the matched `SearchResult`) and `acquisition_state`,
  `local_path` (populated by this slice).
- **FR-002**: Acquisition MUST only attempt a download when
  `state in (VERIFIED, RESOLVED)` and `open_access and pdf_url` are both
  true.
- **FR-003**: A confirmed reference (`VERIFIED`/`RESOLVED`) without an
  open-access URL MUST be marked `PAYWALLED`, never downloaded.
- **FR-004**: A reference that never reached a confirmed state
  (`AMBIGUOUS`/`UNAVAILABLE`) MUST be marked `METADATA_ONLY` and MUST
  remain present in `references.resolved.json` (never removed).
- **FR-005**: Downloads MUST go through an injectable `Downloader`
  Protocol (no direct `httpx` calls in the acquisition function itself),
  so tests never touch the network.
- **FR-006**: A cache under `.cache/downloads/<sha256-of-url>.pdf` MUST be
  checked before calling the downloader; a cache hit MUST NOT invoke the
  downloader again.
- **FR-007**: No paywall-bypass code path may exist anywhere in this
  module (constitution Principle V, non-negotiable).

## Success Criteria

- **SC-001**: An OA fixture reference produces a downloaded file and
  `DOWNLOADED` state.
- **SC-002**: A confirmed non-OA fixture reference produces `PAYWALLED`
  and zero bytes written for it.
- **SC-003**: Calling acquisition twice for the same reference set results
  in exactly one `Downloader.fetch` call (verified via a call-counting
  fake).

## Assumptions

- None beyond what's already recorded in `tech-stack.md` (shared
  `.cache/` layer, §28).
