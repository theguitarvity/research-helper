# Research Helper

Agentic, model-agnostic Research Engineering harness. Chat is ephemeral —
research artifacts are persistent.

## What is Research Helper?

A digital research intern: it searches literature, imports and organizes
papers, extracts and resolves references, validates citations, builds a
citation graph, syncs an Obsidian vault, scaffolds experiments and LaTeX
projects, and hands off state between AI coding agents (Claude Code,
Codex, Copilot, Gemini) — all through the filesystem, so no work depends
on chat history. See `.spec-master/context/app-features.md` for the full
Vertical Slice roadmap and `.spec-master/reports/final-report.md` for
what shipped.

## Architecture

Filesystem-first, script-first: every deterministic operation (hashing,
parsing, manifest generation, dedup, graph/vault generation) lives in the
`research_helper` Python package; the `research-helper` CLI (Typer) is a
thin wrapper over it. A **Research Lab** is any directory containing
`research-helper.yaml` — everything else (`.agent/`, `library/`,
`literature/`, `experiments/`, `papers/`, `graph/`, `vault/`, `logs/`)
hangs off that root. See `.spec-master/context/tech-stack.md` for the
full component breakdown and `.specify/memory/constitution.md` for the
project's non-negotiable principles (model-agnostic, evidence-first,
never fabricate a citation, legal acquisition only, …).

## Installation

Local development (editable, inside this repo):

```bash
uv sync --extra dev
uv run research-helper init
```

Global install (the `research-helper` command becomes available in every
directory, on `PATH`):

```bash
uv tool install --editable .        # from a clone of this repo
# or, once published:
uv tool install research-helper
```

Fallback: `pipx install research-helper`.

Cross-platform bootstrap (checks Python/uv/git, then runs `uv sync`):

```bash
./scripts/bootstrap.sh       # macOS / Linux / Termux
./scripts/bootstrap.ps1      # Windows
```

## Quick Start

```bash
research-helper init                 # scaffold a Research Lab here
research-helper doctor               # check the environment
```

`init` creates `.agent/`, `research/memory/`, `library/`, `literature/`,
`experiments/`, `papers/`, `graph/`, `vault/`, `logs/`, and
`research-helper.yaml`. It's idempotent — safe to re-run.

## Research Workflow (end-to-end example)

```bash
# 1. Search the literature
research-helper search "agentic software engineering" --from 2024 --to 2026

# 2. Import a paper you already have
research-helper import paper-a.pdf --doi 10.1145/1234567 --open-access

# 3. Extract its references
research-helper references extract 10.1145_1234567
# -> "47 references discovered"

# 4. Resolve them against Semantic Scholar / Crossref / OpenAlex
research-helper references resolve 10.1145_1234567
# -> "42 verified, 3 ambiguous, 2 unavailable"

# 5. Download the ones that are legally Open Access
research-helper references download 10.1145_1234567
# -> "38 downloaded, 4 paywalled, 5 metadata_only"

# 6. Persist a structured synthesis (you compute the sections; the CLI
#    only validates + writes them — see "Skills" below for why)
research-helper summarize 10.1145_1234567 --from-json synthesis.json

# 7. Validate the citations (existence + consistency are automatic;
#    claim-support you can supply once you've actually read the claim)
research-helper citations validate 10.1145_1234567 --claims-json claims.json

# 8. Rebuild the citation graph and sync the Obsidian vault
research-helper graph build
research-helper vault sync

# 9. Check everything is structurally sound
research-helper validate
```

## Skills (script vs. agent reasoning)

Every command above either does something fully deterministic (hashing,
parsing, deduping, graph building — no model call, ever) or persists
content *you* computed by actually reading the paper (a synthesis
section, a figure caption, a claim-support judgment). The CLI never
fabricates prose on your behalf: `summarize`, `citations validate
--claims-json`, and figure-analysis calls all take agent-computed content
as input and only handle the deterministic parts (schema, "Not defined
by current context." fallback, persistence). See
`.spec-master/context/app-features.md` Features 8, 9, and 14 for the
exact boundary in each case.

## CLI Reference

```text
research-helper init [PATH]
research-helper doctor
research-helper validate

research-helper import <file.pdf> [--doi DOI] [--source S] [--license L] [--open-access]
research-helper search "<query>" [--from Y] [--to Y] [--sources s1,s2,s3] [--format json]

research-helper references extract <paper-id>
research-helper references resolve <paper-id>
research-helper references download <paper-id>

research-helper summarize <paper-id> --from-json <sections.json>
research-helper citations validate <paper-id> [--claims-json <claims.json>]

research-helper graph build
research-helper vault sync

research-helper experiment init <name> [--title T] [--research-question Q]
                                        [--hypothesis H] [--dataset D]
                                        [--reproduction-command CMD]
research-helper paper init --venue <venue|generic> --name <name>

research-helper handoff create --agent <name> [--status S]
research-helper resume
```

Every command that produces machine-consumable data also supports
`--format json` where applicable (e.g. `search --format json`) — see
`.spec-master/context/app-features.md`'s "Cross-feature requirements"
for the structured-output convention this follows.

## Graphify

`research-helper graph build` derives a file-based citation graph
(`graph/citation-graph.json`) from every imported paper's resolved
references — `Paper` nodes, `CITES` edges — designed to be consumed by a
real Graphify integration later (none was found on this machine at
build time; see `tech-stack.md`'s Integration Points).

## Obsidian

`research-helper vault sync` generates `vault/Papers/<id>.md` notes (with
frontmatter + `[[wikilinks]]` derived only from the citation graph — an
external, non-imported reference renders as plain text, never a broken
link) and refreshes `research/memory/current-context.md`, the compact
checkpoint a new agent reads to pick up where the last one left off.

## Experiments

```bash
research-helper experiment init semantic-cache \
  --research-question "Does semantic caching reduce cost?" \
  --hypothesis "Yes, by more than 30%" \
  --dataset ms-marco \
  --reproduction-command "uv run experiments/semantic-cache/scripts/run.py"
```

Scaffolds `experiments/semantic-cache/` with `README.md`, `hypothesis.md`,
`protocol.md`, `environment/`, `src/`, `scripts/`, `datasets/`, `raw/`,
`results/`, `analysis/`, `figures/`, `logs/`, and a schema-valid
`manifest.yaml` (`EXP-NNN` id, variables, reproduction command).

## LaTeX

```bash
research-helper paper init --venue generic --name harness-engineering
```

Scaffolds `papers/harness-engineering/` (`main.tex`, `references.bib`,
`sections/{introduction,background,methodology,results,discussion,
conclusion}.tex`, `figures/`, `tables/`, `assets/`, `Makefile`,
`README.md`, `venue.json`). `--venue generic` always works out of the
box; any other venue requires a real `venues/<venue>.yaml` you've
registered yourself — Research Helper never fabricates a venue's actual
formatting requirements.

## Cross-Agent Workflow

```bash
research-helper handoff create --agent claude --status in-progress
# ... a different agent, different process, no shared chat history ...
research-helper resume
```

`handoff create` writes `.agent/state/handoff.md` (human-readable) and
`.agent/state/handoff.json` (machine-readable) from one shared record, so
they never disagree. `resume` reconstructs the objective, current task,
open questions, and next steps purely from disk.

## Provenance

Every imported paper carries a provenance record
(`library/papers/<id>/manifest.json`): `source, original_url, doi,
retrieved_at, sha256, license, open_access`. No document's origin is ever
lost, and no reference is presented as verified without a resolved,
independently-checked external record (DOI / OpenAlex ID / Semantic
Scholar ID / arXiv ID) — see the constitution's Principle IV.

## Reproducibility

Experiment manifests record the exact reproduction command; LLM-involving
experiments additionally record `provider`, `model`, `temperature`,
`system_prompt`, `input_artifact`, `output_artifact` when supplied.
Tool version is recorded via `generated_by` in `research-helper.yaml`.

## Troubleshooting

- **`FileNotFoundError: No Research Lab found`** — run `research-helper
  init` first; every other command resolves the lab root from the
  current or an ancestor directory.
- **`research-helper doctor` shows `LaTeX: MISSING`** — install
  `latexmk`/`pdflatex`; LaTeX scaffolding still works, only the `make
  build` step needs it.
- **`research-helper validate` reports issues** — it never silently
  ignores a broken manifest, duplicate DOI, broken wikilink, unbalanced
  BibTeX, broken `\input{}`, missing experiment metadata, or invalid
  handoff; fix the reported path, don't suppress the check.
- **A venue you need isn't registered** — `paper init --venue <name>`
  fails clearly rather than guessing that venue's real formatting rules;
  create `venues/<name>.yaml` yourself with verified requirements first.

## Development

```bash
uv run pytest -q          # 103 tests
uv run ruff check .
uv run mypy research_helper
```
