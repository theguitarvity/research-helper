<!--
Sync Impact Report
- Version change: (none, template) → 1.0.0
- List of modified principles: n/a — initial ratification, no prior version to rename from.
- Added sections: Core Principles (I-VIII), Security & Operational Constraints,
  Development Workflow & Quality Gates, Governance.
- Removed sections: none (template placeholders replaced, no prior content existed).
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ reviewed — its generic "Constitution Check"
    gate already reads from this file at plan time; no template edit needed since it
    has no hardcoded principle names to go stale.
  - .specify/templates/spec-template.md ✅ reviewed — no constitution-specific
    references to reconcile.
  - .specify/templates/tasks-template.md ✅ reviewed — no constitution-specific
    references to reconcile.
  - .specify/templates/commands/*.md — not present in this Spec Kit install (this
    version ships phases as .claude/skills/speckit-*/SKILL.md instead); no file to
    update.
  - README.md ⚠ pending — will be authored in VS001 (Research Lab Foundation) and
    must cite these principles rather than restate them.
- Follow-up TODOs: none — no placeholder was left unresolved.
-->

# Research Helper Constitution

## Core Principles

### I. Model-Agnostic & Cross-Agent Continuity

Research Helper MUST work identically regardless of which coding agent
drives it (Claude Code, OpenAI Codex, GitHub Copilot, Gemini, or any
future agent). No feature MAY require a specific model, provider, or IDE
to function. Work started by one agent MUST be resumable by a different
agent without access to the original chat transcript. Agent-specific
integrations MUST be thin adapters that point at a single canonical
`.agent/` skills/state layer — they MUST NOT duplicate or fork skill
content.
Rationale: this is the project's stated reason to exist (`fundactional.md`
§1, §79) — a Research Helper tied to one vendor defeats its own purpose.

### II. Persistent Artifacts Over Chat History

"Chat is ephemeral. Research artifacts are persistent." The filesystem —
manifests, logs, provenance records, the knowledge graph, and handoff
files — MUST be the source of truth for project context, never the
conversation history. Every command that produces a conclusion, a search
result, or a decision MUST persist it to a file before or instead of only
reporting it in chat.
Rationale: `fundactional.md` §1 (verbatim principle), §16-17 (handoff
must reconstruct context without chat).

### III. Script-First, Token-Conscious Automation

Every deterministic operation (hashing, parsing, DOI/BibTeX handling,
manifest generation, deduplication, vault/graph generation, downloads,
validation) MUST be implemented as a script or library function, never
reproduced manually by an LLM. LLM reasoning is reserved for judgment
calls a script cannot make (synthesis, claim-support assessment,
ambiguity resolution). Token usage MUST follow the priority order:
CLI/script → structured data → local cache → search/retrieval → LLM
reasoning — in that order, before falling back to sending raw documents to
a model.
Rationale: `fundactional.md` §4.1, §5 (explicit pipeline and anti-pattern
examples).

### IV. Evidence-First & Anti-Hallucination (NON-NEGOTIABLE)

Research Helper MUST NOT present a bibliographic reference, a citation
verification, or a scientific claim as trustworthy unless it is backed by
a resolved, external, independently-verifiable record (DOI, OpenAlex ID,
Semantic Scholar ID, arXiv ID, or a verifiable URL). A reference that
cannot be confirmed MUST be marked `UNVERIFIED`; only sustained failure to
verify may escalate it to `SUSPECTED_INVALID`, and accusatory language is
never used automatically. Every conclusion MUST carry provenance and MUST
distinguish `SOURCE FACT`, `AGENT INTERPRETATION`, and `RESEARCHER
DECISION` without mixing them in the same field. Confidence scores MAY
accompany inferential results but MUST NOT substitute for evidence.
Rationale: `fundactional.md` §10, §35, §36, §55 — the context file marks
§55 explicitly "critical."

### V. Legal & Ethical Acquisition

Research Helper MUST NOT implement any paywall-bypass mechanism. Document
acquisition MUST prioritize, in order: Open Access sources, institutional
repositories, preprints, authorized versions, public APIs, and documents
the researcher supplies directly. When a document cannot legally be
downloaded, it MUST be recorded as `METADATA_ONLY` or `PAYWALLED` and
remain in the citation graph rather than being silently dropped. Human
confirmation is REQUIRED before: discarding evidence, definitively
classifying a reference as fraudulent, substantially altering a
hypothesis, submitting or publishing a paper, or any ethically sensitive
or unauthorized-acquisition decision.
Rationale: `fundactional.md` §27, §34.

### VI. Filesystem-First Simplicity

The MVP MUST run locally without Docker, Kubernetes, Kafka, a distributed
database, or a vector/graph database service. Filesystem storage (JSON,
YAML, Markdown) is the default; SQLite MAY be introduced only where a
concrete, demonstrated need exists, never speculatively. Content-
addressable storage and other optimizations are explicitly deferred
post-MVP evaluations, not MVP requirements.
Rationale: `fundactional.md` §42-43, §75, §79 — avoids infrastructure the
project has explicitly ruled out.

### VII. Cross-Platform Portability

Research Helper MUST function on Windows, macOS, Linux, and Android
(via Termux), from one core implementation — "One Core + One CLI + One
Skill Repository + Thin Platform Adapters," never per-OS
reimplementations. All paths MUST be handled through portable path APIs
(`pathlib` in Python) and MUST be persisted workspace-relative, never as
OS-specific absolute paths. Shell scripts (`bash`, `PowerShell`) MUST be
thin bootstrap wrappers only; all real logic lives in the portable
runtime core. Capabilities unavailable on a given platform MUST be
reported explicitly (`CAPABILITY_AVAILABLE` / `_DEGRADED` /
`_UNAVAILABLE`), never silently skipped.
Rationale: `globalization.md` §61, §68-70, §78-79 (explicit design
principle and platform matrix).

### VIII. Researcher Authority & Agent Boundaries

The agent behaves as a research engineering intern: it executes
operational work, organizes evidence, and surfaces inconsistencies, but
it NEVER makes scientific conclusions on the researcher's behalf. The
researcher retains final authority over scientific conclusions and
publication decisions at all times.
Rationale: `fundactional.md` §3, §34.

## Security & Operational Constraints

- Secrets (API keys, tokens, credentials, private datasets, restricted
  papers, personal data) MUST NEVER be committed to version control.
  `.env.example` and `.gitignore` MUST document and enforce this for
  every secret-shaped configuration value.
- Observability logs (`logs/*.jsonl`) MUST record operational metadata
  (task, agent, tool, duration, cache_hit, tokens, status, artifacts) and
  MUST NEVER record secret values.
- All persisted identifiers and paths MUST avoid embedding machine- or
  user-specific absolute paths (`globalization.md` §68).
*(Source: `fundactional.md` §26, §40-41; `globalization.md` §68.)*

## Development Workflow & Quality Gates

- Every skill MUST ship a README following the standard structure defined
  in `fundactional.md` §32 (Purpose … Definition of Done).
- Every CLI command that produces data consumable by another tool or
  agent MUST support structured output (JSON/JSONL/YAML) in addition to
  human-readable Markdown, per `fundactional.md` §30-31.
- `research-helper doctor` (environment/capability detection) and
  `research-helper validate` (structural quality gates: schema validity,
  manifest validity, broken wiki links, duplicate DOIs, missing
  provenance/hashes, invalid BibTeX, broken LaTeX, missing experiment
  metadata, invalid handoff) MUST exist and MUST be runnable offline.
- External APIs (Semantic Scholar, Crossref, OpenAlex, and similar) MUST
  be wrapped behind mockable client interfaces so the automated test
  suite runs deterministically without live network access.
- Operations that do not require network access (graph build, vault sync,
  experiment/LaTeX scaffolding, reference parsing, local search, handoff,
  validation) MUST continue to function fully offline; network-dependent
  operations MUST fail in a controlled, clearly reported way rather than
  crash.
*(Source: `fundactional.md` §32, §48-50; `globalization.md` §73.)*

## Governance

This constitution supersedes any conflicting ad hoc practice. Amendments
require: (1) the proposed change stated in writing with its rationale and
source, (2) a semantic version bump (MAJOR for incompatible principle
removal/redefinition, MINOR for a new or materially expanded principle,
PATCH for wording/clarification), and (3) update of `Last Amended` below.
Any change to a ratified principle that would remove or contradict it
(a `CONFLICT` or `REMOVAL_CANDIDATE` under the Spec Master protocol's
structural diff) MUST be surfaced to the researcher for explicit approval
before being applied — it is never auto-merged. All specifications, plans,
and implementations produced for this project MUST be checked against
these principles before being marked complete; unjustified complexity
(new infrastructure, new dependencies, new services) must cite which
principle it advances or be rejected.

**Version**: 1.0.0 | **Ratified**: 2026-08-27 | **Last Amended**: 2026-08-27
