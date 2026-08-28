---
name: research-helper
description: Agentic, model-agnostic Research Engineering harness — literature search, paper import, reference extraction/resolution, citation validation, citation graph, Obsidian vault, experiment/LaTeX scaffolding, and cross-agent handoff, all via the `research-helper` CLI over a filesystem-first Research Lab.
---

# Research Helper (global Claude Code skill pointer)

Installed globally (`uv tool install --editable <repo>`) so the
`research-helper` command is on `PATH` in every project on this machine,
and this pointer so Claude Code's skill auto-discovery finds it in every
project too. There is no separate "engine mirror" the way `spec-master`
has one — the repo itself is the live install (editable), so a source
change takes effect immediately, no re-sync step needed after editing
code here.

Canonical source:

    /Users/mrlopito/Documents/desenv/ai-projects/skills/ai-research-helper-skill

Read that repo's `README.md` for the full command reference and usage
examples before acting. For the agent persona/behavior boundaries, read
`fundactional.md` §3 (mirrored at `.agent/agents/research-helper/AGENT.md`
inside any initialized Research Lab).

## When to use this skill

The user is doing literature review, citation/reference work, experiment
or LaTeX-paper scaffolding, or wants to hand off research state to a
different agent/session — anything matching `fundactional.md`'s stated
mission (a research engineering intern that organizes evidence,
never substitutes the researcher's scientific judgment, §3).

## How to use it

1. If the current directory isn't already a Research Lab (no
   `research-helper.yaml`), run `research-helper init` first.
2. Drive every operation through the CLI (`research-helper --help` for
   the live command list) — never hand-write a file this CLI would
   produce (manifests, provenance, the citation graph, vault notes,
   handoff files). The tool is script-first: it does the deterministic
   work, you do the reasoning (`fundactional.md` §4.1).
3. Run `research-helper doctor` to check the environment and
   `research-helper validate` before trusting the lab's state after
   manual edits.
4. Before ending a session, `research-helper handoff create --agent
   <your-name>` so a different agent can `research-helper resume` without
   this chat history.
