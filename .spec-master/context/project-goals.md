# Project Goals

## Purpose

Build **Research Helper**, a multimodal, model-agnostic research-engineering
harness that behaves like a digital research intern: it executes
operational, repetitive research work, organizes evidence, prepares
experimental environments, and keeps persistent memory of what was done —
so a researcher never has to reconstruct context by re-reading chat
history. *(EXPLICIT — `fundactional.md` §1)*

## Business / Product Context

The intended user is an individual researcher (or small research group)
running literature review, citation verification, experimentation, and
academic paper writing across multiple AI coding agents (Claude Code,
OpenAI Codex, GitHub Copilot, Gemini) and multiple machines/OSes over the
lifetime of one research project. *(EXPLICIT — §1, §16, §61)*

## Problem Statement

Chat-based agent sessions are ephemeral and single-agent: switching from
Claude to Codex to Gemini today loses irreproducible context (what was
searched, why, what was verified, what remains open), and there is no
durable record of *why* a claim in a paper draft is trustworthy. Manual,
LLM-driven bibliographic work (reading full PDFs to hunt references,
re-deriving what was already extracted) also wastes tokens on work that is
actually deterministic. *(EXPLICIT — §1 "Chat is ephemeral. Research
artifacts are persistent.", §5 Token Economy)*

## Desired Outcome

> Start a research task today with Claude, continue tomorrow with Codex,
> delegate a visual analysis to Gemini, come back to Copilot, and weeks
> later reconstruct exactly what was researched, why, which sources were
> used, which references were verified, which evidence supported which
> decision, which experiments ran, how to reproduce them, which agent
> produced which analysis, and what the next research step is.
> *(EXPLICIT — §60, verbatim)*

## Target Scope

This run's scope (per user override of the context file's own §59 Stop
Condition — see Governance below) is the **full MVP**: all 17 Vertical
Slices in §58 of `fundactional.md`, implemented and demonstrable, plus the
global/cross-platform bootstrap requirements of `globalization.md`.
*(EXPLICIT §58, §77; decision to implement fully is a `USER_DECISION`, not
from the context file — see Governance)*

## Delivery Approach

Filesystem-first, script-first, CLI-thin: deterministic operations
(hashing, parsing, manifest generation, dedup, DOI/BibTeX parsing, vault
generation) live in Python modules and are invoked by a thin CLI; the LLM
orchestrates these tools rather than reproducing their work manually.
Vertical Slices are built and validated independently, in dependency
order. *(EXPLICIT — §4.1, §29, INFERRED delivery-order rationale from §58)*

## What "Done" Means

Per §56 ("Definition of Done — MVP"), *done* means being able to
demonstrate, in order: lab initialization; PDF import; reference
extraction; automatic resolution of a significant share of references;
ambiguous-reference identification; Open Access download; metadata
generation; structured summary generation; citation graph creation;
Obsidian vault sync; topic/period literature search; experiment creation;
LaTeX project creation; `doctor`; `validate`; handoff creation; resumption
of the same Research Task by a different agent; and no mandatory
dependency on chat history. *(EXPLICIT — §56, 18 numbered criteria)*

## Success Criteria

- Reproducibility, Traceability, Evidence, Provenance, Interoperability,
  Automation, Token Efficiency, Model Independence, Researcher Control —
  in that stated priority order. *(EXPLICIT — §60)*
- No fabricated bibliographic reference is ever presented as verified;
  unverifiable references are marked `UNVERIFIED`, never silently dropped
  or silently trusted. *(EXPLICIT — §55, §35, critical requirement)*
- A lab created on one OS opens and continues on another without manual
  migration. *(EXPLICIT — §77)*

## Constraints

- Must be model-agnostic: no fundamental decision may make Research Helper
  depend on one repository, OS, shell, model, IDE, or provider.
  *(EXPLICIT — §79)*
- No Docker dependency, no Kubernetes/Kafka/microservices/distributed DB in
  the MVP. *(EXPLICIT — §43, §79)*
- No paywall bypass mechanisms; only Open Access / institutional
  repositories / preprints / authorized versions / public APIs / documents
  the researcher supplies directly. *(EXPLICIT — §27)*
- Never version secrets (API keys, tokens, credentials, private datasets,
  restricted papers, personal data). *(EXPLICIT — §41)*

## Governance

- The context file (`fundactional.md` §57-59) explicitly scoped the
  *initial* Spec Master run to AUDIT → RESEARCH → ARCHITECTURE →
  SPECIFICATION → ROADMAP only, stopping short of full implementation,
  precisely so architecture/schemas/ADRs/risks would exist before code.
  The user was presented this conflict directly and **explicitly chose to
  override it**, instructing full implementation of all Vertical Slices in
  this same run. This document and `app-features.md`/`tech-stack.md`
  still satisfy the audit/architecture/spec deliverables §57 asks for —
  they are produced first, before any feature's `implement` phase runs —
  so the override changes *how far* this run goes, not the fact that
  architecture precedes implementation for each slice.
  *(EXPLICIT context requirement + USER_DECISION override, both recorded)*
- Constitution conflicts, destructive architectural changes, and repeated
  `analyze` failures still halt for user confirmation per the Spec Master
  protocol — the override authorizes finishing the roadmap, not skipping
  the protocol's own safety gates.

## Risks

- **Scope risk**: 17 Vertical Slices with full literature-search/PDF/graph
  integrations is a large surface for one continuous run; mitigated by
  building real, tested, filesystem-first logic per slice and treating
  live third-party APIs (Semantic Scholar, Crossref, OpenAlex) behind
  thin, mockable client interfaces so slices are demonstrable and testable
  offline, with real HTTP calls as an integration detail. *(INFERRED)*
- **Hallucinated citations**: mitigated structurally per §9/§35/§55 (three
  citation-validation levels, `UNVERIFIED` before `SUSPECTED_INVALID`,
  provenance mandatory on every acquired document). *(EXPLICIT)*
- **Cross-platform drift**: mitigated by `pathlib`-only path handling and a
  single Python core with thin shell wrappers, per §69-§70, §78.
  *(EXPLICIT)*

## Stakeholders

- The researcher (owner/operator of the lab; final authority on scientific
  conclusions, per §3, §34). *(EXPLICIT)*
- The set of coding agents used interchangeably against the same
  workspace: Claude Code, Codex, Copilot, Gemini. *(EXPLICIT §1)*

## Non-goals

- Replacing the researcher's scientific judgment or making unsupervised
  scientific conclusions. *(EXPLICIT §3, §34)*
- Vector databases, graph databases, or distributed infrastructure "because
  they are technically interesting" — filesystem-first is preferred and
  sufficient for the MVP. *(EXPLICIT §42, §75)*
- Paywall bypass / unauthorized acquisition of restricted content.
  *(EXPLICIT §27, §34)*

## Stopping Conditions

O workflow deve ser considerado concluído quando:

- Todas as 17 Vertical Slices (§58) estiverem implementadas, com testes, e
  demonstráveis conforme os critérios do §56 (Definition of Done — MVP).
- Os requisitos de globalização (bootstrap multiplataforma, `doctor`,
  configuração global) estiverem cobertos ao menos no nível descrito nos
  Bootstrap Acceptance Criteria (§77) para macOS (ambiente de execução
  atual), com o design preparado (não necessariamente testado neste
  ambiente) para Windows/Linux/Termux.
- Os quality gates detectados (`gates detect`) passarem, ou falhas não
  bloqueantes estiverem documentadas.
- O relatório final e a matriz de rastreabilidade estiverem publicados em
  `.spec-master/reports/`.

## Source Traceability

| Goal / Constraint | Source | Classification |
|---|---|---|
| Chat is ephemeral; artifacts are persistent | `fundactional.md` §1 | EXPLICIT |
| Model-agnostic, cross-agent continuity | `fundactional.md` §1, §16 | EXPLICIT |
| Script-first / token economy | `fundactional.md` §4.1, §5 | EXPLICIT |
| MVP Definition of Done (18 criteria) | `fundactional.md` §56 | EXPLICIT |
| Success priorities ordering | `fundactional.md` §60 | EXPLICIT |
| No Docker/K8s/distributed infra in MVP | `fundactional.md` §43, §79 | EXPLICIT |
| Legal/ethical acquisition only | `fundactional.md` §27 | EXPLICIT |
| Never version secrets | `fundactional.md` §41 | EXPLICIT |
| Anti-hallucination for citations | `fundactional.md` §55, §35 | EXPLICIT |
| Cross-platform (Win/macOS/Linux/Android) | `globalization.md` §61 | EXPLICIT |
| Original stop-condition (audit-only) | `fundactional.md` §57-59 | EXPLICIT |
| Override to full implementation this run | User instruction (AskUserQuestion) | USER_DECISION |
| Live APIs behind mockable client interfaces | — | INFERRED |
