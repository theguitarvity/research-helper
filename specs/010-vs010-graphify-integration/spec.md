# Feature Specification: Graphify Integration

**Feature dir**: `010-vs010-graphify-integration` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 10 (VS010); `fundactional.md` §12-13

## Scope note

No existing Graphify installation/convention was found on this machine
(`tech-stack.md` Integration Points, `DISCOVERED_FROM_CODEBASE`). This
slice ships a self-contained, file-based graph shaped after §13's node/
relation vocabulary, designed to be consumed by a real Graphify
integration later.

## User Scenarios & Testing

### User Story 1 - Build a citation graph from the library (P1)

**Acceptance Scenarios**:

1. **Given** imported papers with resolved references, **When**
   `graph build` runs, **Then** every paper is a `Paper` node and every
   `VERIFIED`/`RESOLVED` reference produces a `CITES` edge from the
   citing paper to the cited record (an existing library paper if the
   DOI matches one, otherwise an external `Paper` node created for it).
2. **Given** the same library, **When** `graph build` runs twice,
   **Then** the resulting graph is byte-identical (idempotent — it's
   rebuilt fresh from source data each time, never incrementally
   mutated).

### User Story 2 - Answer structural queries (P2)

**Acceptance Scenarios**:

1. **Given** a graph where paper A is cited by B and C, **When**
   `find_seminal_papers` runs, **Then** A ranks above papers cited zero
   times.
2. **Given** a graph with a node no edge touches, **When**
   `find_isolated_nodes` runs, **Then** that node is returned.

## Requirements

### Functional Requirements

- **FR-001**: `GraphNode` (`id, type, properties`) and `GraphEdge`
  (`source, target, type, properties`) MUST use the §13 vocabulary for
  `type` (starting with `Paper` nodes and `CITES` edges; other types are
  supported by the schema but not populated by this slice — no other
  slice yet produces Author/Concept/Claim data).
- **FR-002**: `build_graph(paths)` MUST scan every
  `library/papers/*/manifest.json` + `references.resolved.json`,
  produce one `Paper` node per imported paper, and one `CITES` edge per
  `VERIFIED`/`RESOLVED` reference.
- **FR-003**: A cited reference whose DOI matches an already-imported
  paper MUST link to that paper's existing node id, never create a
  duplicate node for the same DOI.
- **FR-004**: `build_graph` MUST be idempotent: rebuilding from unchanged
  source data MUST produce an identical graph (no incremental state, no
  randomness, deterministic ordering).
- **FR-005**: `graph/citation-graph.json` MUST be written on every build.
- **FR-006**: `find_seminal_papers(graph, top_n)` and
  `find_isolated_nodes(graph, node_type=None)` MUST be pure functions
  over an in-memory `CitationGraph` (no re-reading from disk).

## Success Criteria

- **SC-001**: A 3-paper library (A cites B, C; B cites E) produces a
  graph where `find_seminal_papers` ranks nodes cited by others above
  uncited ones.
- **SC-002**: Rebuilding the same library twice produces identical JSON
  bytes.

## Assumptions

- Only `VERIFIED`/`RESOLVED` references become edges — `AMBIGUOUS`/
  `UNAVAILABLE` references have no confirmed target to link to, so
  they're excluded from graph edges (not from `references.resolved.json`
  itself, which still retains them). *(INFERRED)*
