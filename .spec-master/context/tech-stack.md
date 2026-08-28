# Tech Stack

## Architecture Overview

Filesystem-first, script-first, single Python core, thin CLI, thin
platform adapters — no server, no database beyond optional local SQLite,
no distributed infrastructure. One core package (`research_helper`)
implements every Vertical Slice as an importable module; the CLI (Typer)
is a thin wrapper so the same logic is reachable from any agent's tool
calls without going through a shell. `.agent/` is the single canonical
skills/state layer; `.claude/`, `.codex/`, `.github/`, `.gemini/` contain
only adapters that point back into it — never duplicate content.
*(EXPLICIT — `fundactional.md` §4.1, §6, §29, §42, §78)*

## Languages

- Python 3.12+ — sole implementation language for the core and CLI, per
  explicit stack preference. *(EXPLICIT §42)*
- Bash / PowerShell — thin bootstrap wrappers only, no business logic.
  *(EXPLICIT `globalization.md` §61.3, §70)*

## Frameworks

- **Typer** — CLI framework (explicit preference, §42); gives per-command
  `--format json` support cheaply (structured output requirement, §30).
- **Pydantic** — schema validation for every persisted artifact (search
  results, references, manifests, handoff, experiment manifest) — makes
  "validate structural correctness" (§48) mechanical instead of ad hoc.
- **httpx** — HTTP client for scientific APIs (Semantic Scholar, Crossref,
  OpenAlex); chosen over `requests` because it's explicitly listed (§42)
  and supports both sync and async if search fan-out needs it later.
- **PyYAML** — manifests/venue registry/config that are meant to be
  human-edited (`research-helper.yaml`, `venues/*.yaml`,
  `experiments/*/manifest.yaml`).
- **pytest** — test runner (explicit, §42), with `pytest-mock`/`respx` for
  mocking `httpx` calls in offline tests (§49 "external APIs must have
  mocks for deterministic tests").

## Runtime

- `uv` as the primary environment/dependency manager (`uv sync`, `uv run`,
  `uv tool install research-helper`), with `pipx install research-helper`
  documented as a fallback install path. *(EXPLICIT §42, §61.2)*
- No Docker dependency for the core workflow. *(EXPLICIT §43, §61.2)*

## Infrastructure

- Local filesystem is the primary store for the MVP; SQLite is allowed
  "when useful" but not required by any VS in this MVP — every VS is
  demonstrable purely over JSON/YAML/Markdown files, so SQLite is
  deliberately **not** introduced yet (§75 explicitly defers
  content-addressable/other storage optimizations as post-MVP evaluation).
  *(EXPLICIT §43, §75)*
- Global, OS-convention config/cache directories (`~/.config/research-helper`,
  `~/Library/Application Support/research-helper`, `%APPDATA%\research-helper`)
  layered under a `Project Skill → User Skill → Built-in Skill` override
  chain. *(EXPLICIT §64-§65)*

## Components

### `research_helper.cli`

Typer app; one subcommand group per Vertical Slice
(`search, import, references, citations, summarize, graph, vault, paper,
experiment, handoff, resume, doctor, validate, agents`). Thin: every
command body is `parse args → call core function → render(format)`.

Affected areas: VS001-VS017 (single entrypoint).

### `research_helper.lab`

Workspace resolution + scaffolding (VS001): finds/creates the Research
Lab root, exposes typed paths for every canonical directory.

Affected areas: VS001, and every other component (all of them resolve
paths through this module — never hardcode a path segment elsewhere).

### `research_helper.tasks`

Research Task + session/state model (VS002), backing
`.agent/state/{session,active-task,research-state}.json`.

Affected areas: VS002, VS015 (handoff reads/writes the same state), VS016
(lineage references task/claim IDs).

### `research_helper.search`

Literature search (VS003): one thin client adapter per source
(`SemanticScholarClient`, `CrossrefClient`, `OpenAlexClient`) behind a
common `SearchClient` protocol, normalization + dedup, search-manifest
writer.

Affected areas: VS003, VS004 (import can originate from a search result),
VS006 (resolution reuses the same clients).

### `research_helper.papers`

Paper import + identifier assignment (VS004), provenance recording (§26).

Affected areas: VS004, VS005, VS007, VS008, VS009, VS014.

### `research_helper.references`

Reference extraction, resolution, dedup, BibTeX emission (VS005-VS006).

Affected areas: VS005, VS006, VS007, VS009, VS010.

### `research_helper.acquisition`

Open Access discovery/download + shared `.cache/` layer (VS007, §28).

Affected areas: VS007, VS003/VS006 (share the same cache).

### `research_helper.synthesis`

Structured per-paper and comparative synthesis (VS008).

Affected areas: VS008, VS011 (vault notes embed synthesis), VS016
(claims feed lineage).

### `research_helper.citations`

Three-level citation validation (VS009), confidence-scored classification.

Affected areas: VS009, VS011, VS016.

### `research_helper.graph`

Citation graph builder (VS010), file-based, Graphify-compatible shape.

Affected areas: VS010, VS011 (vault maps derive from the same graph).

### `research_helper.vault`

Obsidian vault generation/sync (VS011) + `research/memory/*` files.

Affected areas: VS011, VS015 (handoff can reference vault state).

### `research_helper.experiments`

Experiment scaffolding + manifest (VS012).

Affected areas: VS012, VS016 (experiments are lineage nodes).

### `research_helper.paper_project`

LaTeX/venue scaffolding (VS013), venue registry loader.

Affected areas: VS013.

### `research_helper.multimodal`

Figure/table extraction as artifacts + capability-delegation tasks
(VS014).

Affected areas: VS014, VS015 (delegation is a handoff-shaped task).

### `research_helper.handoff`

Cross-agent handoff/resume (VS015), `.agent/state/handoff.{md,json}`.

Affected areas: VS015, all others indirectly (every slice's state must be
reconstructible through a handoff).

### `research_helper.lineage`

Research lineage graph (VS016): Question → Search → Papers → Claims →
Hypothesis → Experiment → Evidence → Result → Paper Section.

Affected areas: VS016.

### `research_helper.doctor`

Environment detection, capability matrix, `validate` quality gates,
JSONL observability logging, global config path resolution (VS017).

Affected areas: VS017, and indirectly every slice (validate inspects
every artifact type other slices produce).

## Integration Points

- Semantic Scholar API, Crossref API, OpenAlex API — read-only, public,
  official APIs (§29 "priorizar APIs oficiais"); no scraping.
  *(EXPLICIT)*
- PDF/reference extraction: evaluated rather than hand-built per §42.
  **Decision**: use `pypdf` (or `pdfminer.six`) for raw text extraction and
  a dedicated reference-parsing library (e.g. `GROBID` client when a local
  GROBID service is available, degrading to a regex/heuristic parser
  otherwise) — recorded as `INFERRED`, to be finalized as an ADR in
  Feature 5's `plan` phase once the actual PDF fixtures are in hand; the
  interface (`ReferenceExtractor` protocol) is fixed now so the choice is
  swappable without touching callers. *(INFERRED, pending ADR)*
- Graphify: **no existing Graphify installation or convention was found on
  this machine** (`DISCOVERED_FROM_CODEBASE`: discovery scan found no
  `.graphify`, no prior graph state, no README/CLAUDE.md mentioning it).
  Per §13/§42 ("avaliar compatibilidade... antes de introduzir nova
  tecnologia"), VS010 ships a self-contained, file-based graph
  (nodes/edges as JSON, one file per paper, matching the node/relation
  vocabulary in §13) designed to be consumed by a real Graphify
  integration later, rather than guessing at an external tool's format.
- Obsidian: no plugin/API dependency — a vault is just a directory of
  Markdown files with YAML frontmatter and `[[wikilinks]]`; Obsidian reads
  it natively. *(EXPLICIT §14)*
- LaTeX/BibTeX: shell out to system `latexmk`/`pdflatex`/`bibtex` if
  present; `doctor` reports `MISSING` rather than failing the whole tool
  when absent (§63, §13-of-globalization capability matrix).

## Configuration

- `research-helper.yaml` at the lab root: lab-local settings (default
  search sources, default venue, workflow strategy).
- Global config (`~/.config/research-helper/config.yaml` or OS
  equivalent): API keys/tokens (never committed — §41), default lab path,
  cache location.
- `.env.example` documents every secret-shaped setting without values.

## Technical Constraints

- No fundamental dependency on one OS, shell, model, IDE, provider, Docker,
  or chat history (§79, verbatim list).
- All persisted paths via `pathlib`, always workspace-relative (§69).
- No hardcoded shell-family logic in the core (§70).

## Architectural Principles

- Script what is deterministic; use agents for reasoning (§1, verbatim).
- One Core + One CLI + One Skill Repository + Thin Platform Adapters
  (§78, verbatim) — never "Windows implementation / macOS implementation
  / …".
- Human-readable and machine-readable outputs both maintained, never one
  without the other where both matter (§31).
- Context layering: agents load only the layers (`L0`-`L5`, §46) a task
  needs.

## Testing Strategy

### Unit

Pure functions in every `research_helper.*` module (dedup logic, DOI
normalization, path resolution, schema validation) — no filesystem, no
network.

### Component

Each Vertical Slice's core module against a temp workspace (`tmp_path`
fixture) and mocked HTTP clients (`respx` against `httpx`) — no live
network calls in CI-equivalent runs.

### Integration

CLI commands end-to-end against a scaffolded temp lab, still with mocked
external APIs; validates that CLI → core → filesystem wiring matches the
acceptance criteria in `app-features.md`.

### E2E

The §52-§54 example workflows (`import → extract → resolve → download →
summarize → validate → graph build → vault sync`) run as scripted
integration tests against fixture PDFs bundled in `tests/fixtures/`.

## Quality Gates

- `uv run pytest` (unit + component + integration + e2e-fixture suites).
- `uv run ruff check .` (lint).
- `uv run mypy research_helper` (type-check; Pydantic models make this
  cheap).
- `research-helper validate` (domain-specific structural gate: schemas,
  manifests, wiki links, duplicate DOI, provenance, hashes, BibTeX, LaTeX,
  experiment metadata, handoff — §48, run as part of CI/quality gates,
  not only manually).
- `research-helper doctor` (environment gate, informational — reports
  `MISSING` capabilities, does not fail the build for optional tools like
  LaTeX).

## Repository Conventions

- `.agent/` is the single source of truth for skills/state; `.claude/`
  contains Spec Kit's own skills (`speckit-*`, unrelated to
  `research-helper`'s own agent skills) plus, once created, a
  `research-helper` adapter skill pointing at `.agent/`.
- Every skill directory under `.agent/skills/<name>/README.md` follows the
  §32 template verbatim.
- Conventional, imperative commit messages per feature
  (`feat(vs003): scientific search skill`), matching the "Git as Research
  Memory" convention shape in §44 (`research(literature): …`,
  `experiment(cache): …`) adapted to engineering commits for this build
  phase.

## CI/CD

- No CI provider was detected in discovery (`ci_present: false`). A
  GitHub Actions workflow (`.github/workflows/ci.yml`) running lint + type
  check + tests on push is added as part of VS017 (quality gates must be
  automatable, §48), kept minimal and dependency-light so it doesn't
  require paid API keys to pass (external API tests run against mocks).

## Technical Non-goals

- No vector database, graph database, Kafka, Kubernetes, or microservice
  split in this MVP (§42-§43, §75, §79).
- No custom PDF-parsing engine built from scratch before evaluating
  existing libraries (§42).

## Open Technical Questions

- Final PDF/reference-extraction library pinned in Feature 5's `plan`
  phase after checking what's installable in this environment without
  network access at implement-time; interface frozen now
  (`ReferenceExtractor` protocol) so the pin is swappable.
- Whether to add a real GROBID integration now vs. defer — deferred: GROBID
  requires a running Java service, which conflicts with the "offline-
  first" requirement (`globalization.md` §73) as a hard MVP dependency;
  the heuristic/regex fallback is the default path, GROBID an optional
  enhancement gated behind `doctor` detecting it.

## Source Traceability

| Decision / Constraint | Source | Classification |
|---|---|---|
| Python 3.12+, uv, Typer, Pydantic, PyYAML, httpx, pytest | `fundactional.md` §42 | EXPLICIT |
| Filesystem-first, no vector/graph DB, no distributed infra | `fundactional.md` §42-43, §75, §79 | EXPLICIT |
| One Core + thin adapters design principle | `globalization.md` §78 | EXPLICIT |
| No Docker dependency | `fundactional.md` §43; `globalization.md` §61.2 | EXPLICIT |
| Official scientific APIs only | `fundactional.md` §29 | EXPLICIT |
| No existing Graphify integration on this machine | discovery scan | DISCOVERED_FROM_CODEBASE |
| PDF/reference-extraction library pin | Spec Master evaluation | INFERRED (pending ADR in VS005 plan) |
| GROBID deferred (offline-first conflict) | `globalization.md` §73 | INFERRED |
| GitHub Actions CI added under VS017 | `fundactional.md` §48 (quality gates), no CI found | INFERRED |
