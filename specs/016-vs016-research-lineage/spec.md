# Feature Specification: Research Lineage

**Feature dir**: `016-vs016-research-lineage` (trunk, no branch)
**Created**: 2026-08-27 · **Status**: Draft
**Input**: `app-features.md` Feature 16 (VS016); `fundactional.md` §10, §37

## User Scenarios & Testing

### User Story 1 - Build and walk a lineage chain (P1)

**Acceptance Scenarios**:

1. **Given** nodes for a Research Question, a Paper, a Claim, an
   Experiment, and a Result, linked in that §37 order, **When**
   `trace_back(graph, result_id)` runs, **Then** it returns the full
   chain back to the Research Question, in order.
2. **Given** an attempt to link an edge to a node id that doesn't exist,
   **When** `add_edge` is called, **Then** it raises rather than silently
   creating a dangling reference.

### User Story 2 - Classification is structurally mandatory (P1)

**Acceptance Scenarios**:

1. **Given** any lineage node, **When** it's constructed, **Then**
   `classification` MUST be exactly one of `SOURCE_FACT`,
   `AGENT_INTERPRETATION`, `RESEARCHER_DECISION` — schema-enforced, so a
   node can never mix two of them in the same field (§10, "never mix
   these").

## Requirements

### Functional Requirements

- **FR-001**: `LineageNode` MUST have `id, type, classification,
  properties`, with `type` drawn from §37's chain vocabulary (Research
  Question, Literature Search, Paper, Claim, Hypothesis, Experiment,
  Evidence, Result, Paper Section) and `classification` a required
  `Literal["SOURCE_FACT", "AGENT_INTERPRETATION", "RESEARCHER_DECISION"]`.
- **FR-002**: `add_edge(graph, source_id, target_id)` MUST raise
  `KeyError` if either id isn't already a node in the graph.
- **FR-003**: `trace_back(graph, node_id)` MUST return every ancestor
  reachable by following edges backward, ordered from the given node back
  to its root(s).
- **FR-004**: `save_lineage`/`load_lineage` MUST persist/reload
  `graph/research-lineage.json` losslessly.

## Success Criteria

- **SC-001**: A 5-node chain (Question→Paper→Claim→Experiment→Result)
  traces back from Result to Question, in order, via `trace_back`.
- **SC-002**: `add_edge` to an unknown id raises `KeyError`.
- **SC-003**: An invalid `classification` value is rejected at
  construction time.

## Assumptions

None beyond §37's chain vocabulary, which is explicit.
