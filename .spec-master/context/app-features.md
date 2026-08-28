# App Features

## Context

Research Helper is a filesystem-first research-engineering harness. Each
feature below is one Vertical Slice from `fundactional.md` §58 (refined
with the cross-cutting globalization requirements from `globalization.md`
where they change a slice's acceptance criteria). Slices are independently
demonstrable and are implemented in dependency order (see
`features order` in the final report).

## Scope

In scope: the CLI (`research-helper`), all 17 Vertical Slices, the shared
`.agent/` skills layer, Obsidian vault generation, Graphify-compatible
citation graph, LaTeX/venue scaffolding, experiment scaffolding, doctor/
validate/observability, and cross-platform bootstrap. Out of scope for
this MVP: any GUI, any hosted service, any distributed backend, any
paywall-bypass mechanism.

## Features

### Feature 1 — VS001 Research Lab Foundation

#### Objective

Turn any directory into a Research Lab: canonical folder layout, portable
paths, global CLI entrypoint, and the `.agent/` canonical skills layer that
every downstream slice and every agent adapter reads from.

#### Expected behavior

- `research-helper init [path]` scaffolds `.agent/`, `research/`,
  `library/`, `literature/`, `experiments/`, `papers/`, `graph/`, `vault/`,
  `logs/`, and `research-helper.yaml` at `path` (default: cwd).
- Workspace resolution order: current directory → nearest Research Lab
  root → user global config.
- All persisted paths are workspace-relative (`pathlib`), never absolute
  or OS-specific.

#### Acceptance criteria

- [ ] `research-helper init` is idempotent (safe to re-run; never
      clobbers existing content).
- [ ] `research-helper init ~/research/x` initializes at an explicit path.
- [ ] No path written to any manifest is absolute or contains `\`.
- [ ] `.agent/` contains `agents/research-helper/`, `skills/`, `scripts/`,
      `schemas/`, `templates/`, `state/`, `adapters/`.

#### Test scenarios

- Init into an empty dir; init into a dir that already has some of the
  folders (idempotency); init at a nested explicit path that doesn't exist
  yet (parents auto-created).

---

### Feature 2 — VS002 Research Task + State

#### Objective

Model a Research Task as a first-class, agent-independent unit of work
with explicit status and step tracking, backed by `.agent/state/`.

#### Expected behavior

- A Research Task (`RT-NNN`) has `type`, `objective`, `inputs`, `status`,
  `steps`, `artifacts`, `agent_history`.
- `.agent/state/session.json`, `active-task.json`, `research-state.json`
  track current session/task state independent of any chat transcript.

#### Acceptance criteria

- [ ] Creating a task persists it under `.agent/state/`; reading it back
      after "restarting the agent" (fresh process) reconstructs the same
      task.
- [ ] `agent_history` accumulates every agent that touched the task.
- [ ] No required field silently defaults without being recorded.

#### Test scenarios

- Create task with `claude`, simulate handoff by appending `codex` to
  `agent_history`, reload from disk, assert both present.

---

### Feature 3 — VS003 Scientific Search

#### Objective

Skill `research-helper/literature-search`: structured scientific search
across Semantic Scholar, Crossref, OpenAlex, normalized to one schema.

#### Expected behavior

- Input: query, date range, languages, max_results, sources (per schema in
  §7).
- Output: normalized records (`title, authors, year, doi, venue, abstract,
  url, pdf_url, open_access, source`).
- Dedup priority: DOI → normalized title → authors+year.
- Every search persists a reproducible search manifest under
  `literature/searches/<date>-<slug>/` (`query.yaml`, `raw-results.json`,
  `normalized.json`, `selected.json`, `README.md`) per §38.

#### Acceptance criteria

- [ ] `research-helper search "<query>" --from Y --to Y --format json`
      returns deduplicated, schema-conformant results.
- [ ] Search manifest is written and is re-executable (re-running
      `query.yaml` reproduces the same query parameters).
- [ ] Network calls go through mockable client adapters (one per source)
      so tests run offline.

#### Test scenarios

- Mocked multi-source query with overlapping DOIs → dedup verified;
  offline mode with only cached results.

---

### Feature 4 — VS004 Paper Import

#### Objective

Import a PDF (or metadata-only record) into `library/papers/` under a
stable identifier.

#### Expected behavior

- Identifier: DOI-normalized (`10.1145_1234567/`) when a DOI is known,
  else `paper-{normalized-hash}/` (§25).
- Each paper directory: `paper.pdf`, `metadata.json`, `references.json`,
  `summary.md`, `claims.json`, `manifest.json`.
- Provenance recorded per §26 schema (`source, original_url, doi,
  retrieved_at, sha256, license, open_access`) on every import.

#### Acceptance criteria

- [ ] `research-helper import paper.pdf` creates the identifier directory
      with `sha256` provenance recorded.
- [ ] Re-importing the same file is detected (hash match) and does not
      duplicate storage.
- [ ] Import without a resolvable DOI falls back to the hash-based
      identifier without failing.

#### Test scenarios

- Import with known DOI in metadata; import with no DOI (hash fallback);
  re-import of an identical file.

---

### Feature 5 — VS005 Reference Extraction

#### Objective

Skill `research-helper/reference-harvester` (extraction half): given
`paper.pdf`, produce `references.raw.json` and `references.normalized.json`
via the pipeline in §8 (text/structured extraction → reference-section
detection → parsing → DOI extraction).

#### Expected behavior

- Uses a specialized PDF/reference-extraction library evaluated in
  `tech-stack.md` rather than a hand-rolled parser (§42).
- Each raw reference gets an initial state of `DISCOVERED`.

#### Acceptance criteria

- [ ] `research-helper references extract <paper>` reports a count
      ("N references discovered") matching §52's example shape.
- [ ] Extraction is deterministic given the same PDF (no LLM call needed
      for this step, per §4.1 script-first).
- [ ] Output validates against the reference schema.

#### Test scenarios

- Fixture PDF with a known reference count; PDF with no detectable
  reference section (graceful `0 discovered`, not a crash).

---

### Feature 6 — VS006 Reference Resolution

#### Objective

Resolve each raw reference to a real, external, verifiable document
(`references.resolved.json`), assigning one of the states in §8
(`RESOLVED, VERIFIED, AMBIGUOUS, UNAVAILABLE, INVALID`) using independent
external sources, never trusting the citing paper alone (§35).

#### Expected behavior

- Bibliographic-consistency check (§9 Level 2): mismatched
  author/year/venue between citation and resolved record is flagged, not
  silently accepted.
- Unresolvable references are `UNVERIFIED`, never silently dropped.

#### Acceptance criteria

- [ ] `research-helper references resolve <paper>` reports counts matching
      the §52 shape (verified / ambiguous / unavailable / unresolved).
- [ ] A citation year mismatch (e.g. "Smith et al., 2021" resolving to a
      2020 record) is surfaced as a flagged inconsistency, not silently
      corrected.
- [ ] `references.bib` is emitted alongside the JSON.

#### Test scenarios

- Fixture with a deliberately mismatched citation year; fixture with an
  ambiguous multi-candidate title.

---

### Feature 7 — VS007 Open Access Acquisition

#### Objective

Download resolved references only when legally available (§27), recording
`METADATA_ONLY` or `PAYWALLED` otherwise, with caching (§28).

#### Expected behavior

- Priority order: Open Access → institutional repository → preprint →
  authorized version → public API → researcher-supplied.
- No paywall-bypass code path exists.
- `.cache/{crossref,openalex,semantic-scholar,metadata,extraction}/` avoids
  redundant external calls for identical queries.

#### Acceptance criteria

- [ ] `research-helper references download <paper>` only writes a PDF for
      references marked open-access-available; others get
      `PAYWALLED`/`METADATA_ONLY` and remain in the graph.
- [ ] Second run against the same references is a cache hit (no duplicate
      network calls in test doubles).

#### Test scenarios

- Mixed batch of OA/paywalled fixtures; repeated download call verifying
  cache short-circuit.

---

### Feature 8 — VS008 Structured Paper Synthesis

#### Objective

Skill `research-helper/paper-synthesizer`: produce the full structured
synthesis schema from §11 (not a generic summary), plus multi-paper
comparison artifacts.

#### Expected behavior

- Per-paper: `synthesis/individual/<paper-id>.md` with all §11 sections
  (Metadata … Researcher's Notes).
- Cross-paper: `comparison.md`, `disagreements.md`, `common-findings.md`,
  `research-gaps.md`.

#### Acceptance criteria

- [ ] `research-helper summarize <paper>` produces a synthesis file with
      every §11 section present (marked "Not defined by current context."
      where the paper doesn't support a section, never fabricated).
- [ ] Comparative synthesis across ≥2 papers produces all four
      cross-paper artifacts.

#### Test scenarios

- Single-paper synthesis from a fixture with sparse metadata (sections
  correctly marked not-applicable, not invented).

---

### Feature 9 — VS009 Citation Validation

#### Objective

Skill `research-helper/citation-validator`: the three-level evaluation from
§9 (Existence, Bibliographic Consistency, Claim Support), always with
evidence, justification, and confidence (§36), never presented as
absolute truth.

#### Expected behavior

- Level 3 classification ∈ `{SUPPORTED, PARTIALLY_SUPPORTED, NOT_SUPPORTED,
  CONTRADICTED, UNCLEAR}`.
- Verification state precedes accusation: `UNVERIFIED` before
  `SUSPECTED_INVALID` (§35), never accusatory language.

#### Acceptance criteria

- [ ] `research-helper citations validate <paper>` emits a Level 1/2/3
      result per citation with stored evidence + confidence.
- [ ] No citation is ever labeled `SUSPECTED_INVALID` without first passing
      through `UNVERIFIED`.

#### Test scenarios

- Citation whose claim is contradicted by the cited paper's own findings
  (fixture); citation with no supporting evidence found (→ `UNCLEAR`, not
  `NOT_SUPPORTED`, since absence of evidence ≠ evidence of absence per
  spirit of §9/§35 — recorded as an explicit modeling decision, INFERRED).

---

### Feature 10 — VS010 Graphify Integration

#### Objective

Feed the citation graph (§12) into Graphify: nodes/edges for
`CITES`-style paper relations, extensible to the full node/relation
vocabulary in §13.

#### Expected behavior

- `research-helper graph build` derives graph data from
  `references.resolved.json` across the library — no separate
  hand-maintained graph state.
- Graph representation is compatible with whatever the existing Graphify
  project expects (evaluated in `tech-stack.md`; filesystem-based if no
  existing Graphify integration convention is found on this machine).

#### Acceptance criteria

- [ ] `research-helper graph build` is re-runnable and idempotent
      (rebuilding from the same library yields the same graph).
- [ ] Graph queries "find seminal papers" / "find isolated claims" (§12)
      are answerable from the built graph without re-parsing PDFs.

#### Test scenarios

- Small library (A cites B, C; B cites E) → graph build → traverse from A.

---

### Feature 11 — VS011 Obsidian Research Memory

#### Objective

Skill `research-helper/graphify-research` counterpart for humans: generate/
sync an Obsidian-compatible vault (§14) from the same underlying data, and
research memory files (§15).

#### Expected behavior

- `vault/{Papers,Authors,Concepts,Claims,Experiments,Datasets,Methods,
  Questions,Daily,Maps}/` generated by script, not by the LLM hand-writing
  links (§14, explicit).
- Each paper note has the exact frontmatter/section shape from §14,
  including `[[wikilinks]]` to references and concepts.
- `research/memory/current-context.md` lets a new agent understand active
  research state without reading the whole lab (§15, §45).

#### Acceptance criteria

- [ ] `research-helper vault sync` is idempotent and derives links only
      from resolved data (no invented `[[links]]`).
- [ ] `current-context.md` answers all 7 bullet points listed in §15.

#### Test scenarios

- Sync with a paper that cites another already-imported paper → wikilink
  present and correct; re-sync with no changes → no diff.

---

### Feature 12 — VS012 Experiment Scaffolder

#### Objective

`research-helper experiment init <name>` scaffolds the structure and
manifest from §21-§23, maximizing reproducibility.

#### Expected behavior

- Structure exactly as §21 (`README.md, hypothesis.md, protocol.md,
  environment/, src/, scripts/, datasets/, raw/, results/, analysis/,
  figures/, logs/, manifest.yaml`).
- `manifest.yaml` matches the §22 schema; LLM-involving experiments record
  the extra provider/model/temperature/system-prompt/input/output fields
  from §23 when available.

#### Acceptance criteria

- [ ] `research-helper experiment init <name>` creates the full structure
      with a valid, schema-conformant `manifest.yaml`.
- [ ] Reproduction command recorded in the manifest is the literal command
      needed to reproduce the run.

#### Test scenarios

- Init a non-LLM experiment (baseline fields only); init an LLM-involving
  experiment (extra fields populated, not left blank when info is known).

---

### Feature 13 — VS013 LaTeX / Venue Scaffolder

#### Objective

`research-helper/latex-scaffolder` + venue registry (§19-§20):
`research-helper paper init --venue <v> --name <n>` scaffolds an academic
LaTeX project against a registered, provenance-tracked venue template.

#### Expected behavior

- Output structure exactly as §19.
- `venues/<venue>.yaml` separates `requirements` (verified) from agent
  assumptions, per §20's explicit split; never invents formatting
  requirements.
- Templates under `templates/latex/{generic,sbpc,wop,sbc,ieee,acm,custom}/`
  preserve license/provenance of official sources.

#### Acceptance criteria

- [ ] `paper init --venue wop --name x` fails clearly (not silently) if
      `venues/wop.yaml` doesn't exist yet, rather than fabricating
      requirements.
- [ ] Generated project builds with the scaffolded `Makefile` (or reports
      `LATEX MISSING` per the doctor matrix rather than crashing).

#### Test scenarios

- Init against the bundled `generic` venue; init against an unregistered
  venue name (clear, non-fabricating failure).

---

### Feature 14 — VS014 Multimodal Artifacts

#### Objective

Treat figures/tables as first-class entities (§39) and record explicit
capability degradation when the active model/agent lacks multimodal
support (§18), instead of silently skipping analysis.

#### Expected behavior

- Figure extraction: `figure-NNN.png` + `figure-NNN.json`
  (`paper, page, figure, caption, extraction_method, analysis_model`) +
  `analysis.md`, persisted as artifacts, not just returned in chat (§18,
  explicit).
- When the current agent can't do the needed visual reasoning, a
  multimodal delegation task is created (§18 example: Codex → Gemini →
  Codex resumes) instead of silently degrading.

#### Acceptance criteria

- [ ] Every extracted figure/table has both the human file and the
      structured JSON sidecar.
- [ ] A capability gap creates a recorded delegation task
      (`CAPABILITY_UNAVAILABLE`), never a silent skip.

#### Test scenarios

- Extract a labeled figure from a fixture PDF; simulate a
  non-multimodal-capable agent context and assert a delegation task file
  is produced.

---

### Feature 15 — VS015 Cross-Agent Handoff

#### Objective

The Omni Router / Cross-Agent Continuity requirement (§16-§17): persist
enough state in `.agent/state/handoff.md` + `handoff.json` that a
different agent/model resumes without chat history.

#### Expected behavior

- `research-helper handoff create` writes both files with every section
  from §16's `handoff.md` template and every field from §17's
  `handoff.json` schema.
- `research-helper resume` reads the latest handoff and reconstructs
  session context (Step in Agent Session Bootstrap, §45).

#### Acceptance criteria

- [ ] `handoff create` → (simulate fresh agent/process) → `resume`
      reconstructs objective, current task, open questions, and next
      steps without any other input.
- [ ] `handoff.md` and `handoff.json` never diverge on the facts they both
      represent (single source generates both).

#### Test scenarios

- Full round-trip: do work → `handoff create` → wipe in-memory
  state → `resume` → assert reconstructed state matches.

---

### Feature 16 — VS016 Research Lineage

#### Objective

Maintain the lineage chain from §37 (Research Question → Literature Search
→ Papers → Claims → Hypothesis → Experiment → Evidence → Result → Paper
Section) so "where did this claim in our paper come from?" is answerable,
building on the evidence-first model (§10) and provenance (§26).

#### Expected behavior

- Every claim used in paper writing links back through the chain to a
  resolved source paper and stored evidence — never a bare assertion.
- Distinguishes `SOURCE FACT` / `AGENT INTERPRETATION` / `RESEARCHER
  DECISION` explicitly at every lineage node (§10, "never mix these").

#### Acceptance criteria

- [ ] Given a paper-section claim, the lineage can be walked backward to
      its originating evidence and resolved paper.
- [ ] No lineage node mixes a `SOURCE FACT` with an `AGENT INTERPRETATION`
      in the same field.

#### Test scenarios

- Build a 3-hop lineage (question → paper → claim → experiment → result)
  from fixtures and walk it end to end.

---

### Feature 17 — VS017 Doctor / Validation / Observability

#### Objective

`research-helper doctor` and `research-helper validate` (§48, §63), plus
structured observability logs (§40) and the cross-platform bootstrap
requirements from `globalization.md` (§61-§79): global CLI, bootstrap
scripts, platform capability matrix, global config/cache.

#### Expected behavior

- `doctor` reports exactly the shape in §63 (Platform / Core / Research /
  Academic / Agents / Status) and validates the Platform Capability Matrix
  from `globalization.md` §62.
- `validate` runs the quality-gate checks from §48 (schema validity,
  manifest validity, broken wiki links, duplicate DOI, missing
  provenance/hashes, invalid BibTeX, broken LaTeX, missing experiment
  metadata, invalid handoff).
- `logs/{research-helper,agents,tools,errors}.jsonl` record task/agent/
  tool/duration/cache_hit/tokens/status/artifacts, never secrets (§40-41).
- Global config resolved per OS convention (`~/.config/research-helper` on
  Linux/Android, `~/Library/Application Support/research-helper` on
  macOS, `%APPDATA%\research-helper` on Windows) — §64.
- `scripts/bootstrap.{py,sh,ps1}` with `bootstrap.py` holding the
  cross-platform logic and the shell/PowerShell files as thin wrappers,
  matching the “One Core” design principle (§78).

#### Acceptance criteria

- [ ] `research-helper doctor` runs on macOS (this environment) and
      reports accurate OS/arch/shell/tool detection.
- [ ] `research-helper validate` fails loudly (non-zero exit, itemized
      report) on at least one deliberately broken fixture per gate type.
- [ ] No log line contains a secret value.
- [ ] Global config path resolution is implemented for all four OS
      branches even though only macOS is exercised live in this
      environment (Windows/Linux/Termux verified by unit test against
      injected `sys.platform`, not live execution — recorded as a known
      limitation, not silently claimed as tested).

#### Test scenarios

- `doctor` against this machine (live); `doctor`/config-path resolution
  against mocked `sys.platform` values for the other three OSes;
  `validate` against fixtures with each individual defect class.

## Cross-feature requirements

- Every skill follows the README standard in §32 (`Purpose … Definition of
  Done`), reusing that convention across all `.agent/skills/*/README.md`.
- Structured output (JSON/JSONL/YAML/Markdown) available wherever a CLI
  command can be consumed by another tool or agent, per §30-§31 — Markdown
  for the researcher, structured data for agents/automation, both kept in
  sync.
- Context layering (§46-§47): agents load only the layers a task needs
  (L0 Constitution … L5 Raw Artifacts), never the whole lab.
- Path portability (`globalization.md` §68-§69): no absolute,
  OS-specific path is ever persisted to a manifest, handoff, or vault
  note.

## Quality requirements

- Reproducibility, Traceability, Evidence, Provenance, Interoperability,
  Automation, Token Efficiency, Model Independence, Researcher Control —
  §60 priority order applies to every feature's design trade-offs.
- Deterministic operations must not require an LLM call (§4.1); LLM
  reasoning is reserved for synthesis/judgment steps that scripts cannot
  make deterministically.

## Non-goals

- GUI, hosted backend, distributed infrastructure (§43, §75, §79).
- Paywall bypass (§27, §34).
- Fabricated bibliographic references from model memory alone (§55).

## Dependencies

- VS002 depends on VS001 (state lives under `.agent/` from VS001).
- VS004-VS009 depend on VS001-VS002 (need the lab + task model to attach
  imported papers/results to).
- VS010-VS011 depend on VS005-VS009 (graph/vault are derived views over
  resolved references, synthesis, and citation validation).
- VS012, VS013 depend on VS001-VS002 only (independent scaffolds).
- VS014 depends on VS004 (needs imported papers to extract figures from).
- VS015-VS016 depend on the full data model existing (VS002-VS011).
- VS017 depends on all prior slices existing to have something to
  validate/observe, but its bootstrap/global-config sub-scope only
  depends on VS001.
- *(EXPLICIT: dependency direction implied by data flow in §52-§54;
  exact ordering INFERRED and resolved by `features order`.)*

## Open questions

- Which specialized PDF/reference-extraction library to standardize on —
  resolved in `tech-stack.md` (Technology Evaluation) rather than left
  open, per §42's instruction to evaluate before building manual parsers.
- Whether an existing Graphify project/convention exists on this machine
  to integrate with — none was found during discovery (fresh environment);
  recorded as `DISCOVERED_FROM_CODEBASE: none found`, so VS010 ships a
  self-contained, file-based graph representation designed to be Graphify-
  compatible rather than a live integration.

## Source traceability

| Requirement | Source | Classification |
|---|---|---|
| 17 Vertical Slices | `fundactional.md` §58 | EXPLICIT |
| MVP Definition of Done | `fundactional.md` §56 | EXPLICIT |
| Skill schemas per section (§7-§23) | `fundactional.md` §7-§23 | EXPLICIT |
| Doctor/validate/global bootstrap | `globalization.md` §61-§79 | EXPLICIT |
| No existing Graphify integration found | discovery scan | DISCOVERED_FROM_CODEBASE |
| Feature dependency ordering | derived from data flow | INFERRED |
| PDF/reference library choice | `tech-stack.md` | INFERRED (resolved there) |
