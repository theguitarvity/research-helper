# Research Helper

Agentic, model-agnostic Research Engineering harness. Chat is ephemeral —
research artifacts are persistent.

> This README grows with each Vertical Slice as the project is built.
> Full sections (Architecture, Installation, Skills, CLI, Graphify,
> Obsidian, Experiments, LaTeX, Cross-Agent Workflow, Provenance,
> Reproducibility, Troubleshooting) land as those slices are implemented —
> see `.spec-master/context/app-features.md` for the full roadmap.

## What is Research Helper?

A digital research intern: it searches literature, imports and organizes
papers, extracts and resolves references, validates citations, builds a
citation graph, syncs an Obsidian vault, scaffolds experiments and LaTeX
projects, and hands off state between AI coding agents (Claude Code,
Codex, Copilot, Gemini) — all through the filesystem, so no work depends
on chat history.

## Installation

```bash
uv sync --extra dev
uv run research-helper init
```

## Quick Start

```bash
uv run research-helper init
```

Scaffolds a Research Lab in the current directory (`.agent/`, `research/`,
`library/`, `literature/`, `experiments/`, `papers/`, `graph/`, `vault/`,
`logs/`, `research-helper.yaml`).
