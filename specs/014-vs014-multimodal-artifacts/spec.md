# Feature Specification: Multimodal Artifacts

**Feature dir**: `014-vs014-multimodal-artifacts` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 14 (VS014); `fundactional.md` §18, §39

## Architecture note

Extracting embedded images from a PDF is mechanical (deterministic,
via `pypdf`'s image API — injectable for testing, matching the
`SearchClient`/`Downloader` pattern used elsewhere). Writing a caption or
visual *analysis* of a figure requires actually looking at the image —
reasoning work for a multimodal-capable agent (constitution Principle
III), so this module persists agent-supplied analysis, it does not
generate it.

## User Scenarios & Testing

### User Story 1 - Extract figures as first-class artifacts (P1)

**Acceptance Scenarios**:

1. **Given** a paper's PDF with embedded images, **When**
   `extract_images` runs, **Then** each image is saved as
   `figures/figure-NNN.png` with a `figures/figure-NNN.json` sidecar
   (`paper, page, figure, caption: null, extraction_method,
   analysis_model: null`) and an empty `figures/figure-NNN.analysis.md`
   placeholder — never a fabricated caption or analysis.
2. **Given** an extracted figure, **When** `record_figure_analysis`
   supplies a caption/analysis, **Then** the sidecar and analysis file
   are updated with exactly that content.

### User Story 2 - Explicit capability delegation (P1)

**Acceptance Scenarios**:

1. **Given** the current agent lacks multimodal capability for a needed
   analysis, **When** `create_delegation_task` is called, **Then** a
   `.agent/state/delegations/<id>.json` record with state
   `CAPABILITY_UNAVAILABLE` is written — never a silent skip.

## Requirements

### Functional Requirements

- **FR-001**: `extract_images(paper_dir, reader=None)` MUST accept an
  injectable PDF-reader-like object (defaulting to a real `pypdf.PdfReader`
  over the paper's PDF) so tests never depend on hand-crafting real
  embedded-image bytes.
- **FR-002**: Each extracted image MUST produce
  `figures/figure-NNN.{ext}`, `figures/figure-NNN.json`, and
  `figures/figure-NNN.analysis.md`, with `caption`/`analysis_model` null
  and the analysis file containing only the standard not-defined marker.
- **FR-003**: `record_figure_analysis(paper_dir, figure_id, ...)` MUST
  update only the fields it's given, never invent the rest.
- **FR-004**: `create_delegation_task(paths, *, capability, reason)`
  MUST write a `CAPABILITY_UNAVAILABLE` record; MUST NOT silently no-op.

## Success Criteria

- **SC-001**: A fake reader with 2 images across 2 pages produces exactly
  2 numbered figure triples.
- **SC-002**: `record_figure_analysis` changes only the fields passed to
  it.
- **SC-003**: Every `create_delegation_task` call produces a discoverable
  file (`.agent/state/delegations/*.json`).

## Assumptions

- §39's tree diagram shows one shared `analysis.md`; this slice uses
  `figure-NNN.analysis.md` per figure instead, since a single shared file
  can't correspond 1:1 to multiple figures in one paper. *(INFERRED,
  explicitly flagged)*
