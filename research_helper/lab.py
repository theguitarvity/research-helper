"""Research Lab workspace resolution and scaffolding (VS001).

Filesystem-first, script-first (constitution Principle III): every
directory this module creates is deterministic, no LLM involved. All
paths are built with ``pathlib`` and, wherever they are persisted, are
written workspace-relative (constitution Principle VII).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from research_helper import __version__

MANIFEST_NAME = "research-helper.yaml"

# Directories created by `init`, relative to the lab root.
# fundactional.md §6 (.agent/ canonical skills layer) + §24 (lab layout).
LAB_SUBDIRS: tuple[str, ...] = (
    ".agent/agents/research-helper",
    ".agent/skills",
    ".agent/scripts",
    ".agent/schemas",
    ".agent/templates",
    ".agent/state",
    ".agent/adapters",
    "research/memory",
    "library/papers",
    "library/books",
    "library/articles",
    "library/datasets",
    "literature/searches",
    "literature/references",
    "literature/synthesis",
    "experiments",
    "papers",
    "graph",
    "vault",
    "logs",
)


# fundactional.md §3 (Persona do agente) — verbatim role definition, EXPLICIT.
AGENT_MD_CONTENT = """\
# Research Helper Agent

## Persona

`research-helper` behaves as a **Research Assistant / Research
Engineering Intern**. It does not replace the researcher in scientific
decision-making.

## Role

- Execute operational research work.
- Collect evidence.
- Organize literature.
- Prepare material.
- Structure experiments.
- Verify information.
- Synthesize content.
- Maintain traceability.
- Raise inconsistencies.
- Present evidence for human decision.

The researcher remains responsible for scientific conclusions.

## Boundaries

Human confirmation is required before: important scientific conclusions,
discarding evidence, definitively classifying a reference as fraudulent,
substantially altering a hypothesis, submitting or publishing a paper, or
any ethical or unauthorized-acquisition decision.
"""

AGENT_README_CONTENT = """\
# research-helper agent definition

This directory holds the canonical persona/behavior definition for the
`research-helper` agent (`AGENT.md`). Every platform adapter
(`.claude/`, `.codex/`, `.github/`, `.gemini/`) points back here rather
than duplicating this content.
"""


def default_manifest() -> dict:
    return {
        "generated_by": {"tool": "research-helper", "version": __version__},
        "workflow": {
            "default_search_sources": ["semantic-scholar", "crossref", "openalex"],
            "default_venue": None,
        },
    }


def scaffold(root: Path) -> Path:
    """Create every missing canonical directory/file under ``root``.

    Idempotent: never truncates or deletes anything that already exists
    (FR-003). Returns the resolved lab root.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    for rel in LAB_SUBDIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)

    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        manifest_path.write_text(
            yaml.safe_dump(default_manifest(), sort_keys=False),
            encoding="utf-8",
        )

    agent_def_dir = root / ".agent" / "agents" / "research-helper"
    agent_md = agent_def_dir / "AGENT.md"
    if not agent_md.exists():
        agent_md.write_text(AGENT_MD_CONTENT, encoding="utf-8")
    agent_readme = agent_def_dir / "README.md"
    if not agent_readme.exists():
        agent_readme.write_text(AGENT_README_CONTENT, encoding="utf-8")

    return root


def is_lab_root(path: Path) -> bool:
    return (Path(path) / MANIFEST_NAME).is_file()


def resolve_lab_root(start: Path | None = None) -> Path | None:
    """Current directory -> nearest ancestor with a manifest -> None.

    The `None` fallback stands in for "user global configuration" here;
    VS017 (Doctor / Global Config) is what actually reads a global config
    file and is expected to call this first and only fall back itself.
    """
    current = Path(start or Path.cwd()).resolve()
    if is_lab_root(current):
        return current
    for ancestor in current.parents:
        if is_lab_root(ancestor):
            return ancestor
    return None


@dataclass(frozen=True)
class LabPaths:
    """Typed accessor for every canonical Research Lab directory.

    Every later Vertical Slice resolves paths through this class rather
    than reconstructing path segments itself (constitution Principle VII).
    """

    root: Path

    @classmethod
    def resolve(cls, start: Path | None = None) -> LabPaths:
        root = resolve_lab_root(start)
        if root is None:
            raise FileNotFoundError(
                "No Research Lab found (no research-helper.yaml in the "
                "current directory or any ancestor). Run `research-helper "
                "init` first."
            )
        return cls(root=root)

    @property
    def manifest_path(self) -> Path:
        return self.root / MANIFEST_NAME

    @property
    def agent_dir(self) -> Path:
        return self.root / ".agent"

    @property
    def agent_definition_dir(self) -> Path:
        return self.agent_dir / "agents" / "research-helper"

    @property
    def skills_dir(self) -> Path:
        return self.agent_dir / "skills"

    @property
    def scripts_dir(self) -> Path:
        return self.agent_dir / "scripts"

    @property
    def schemas_dir(self) -> Path:
        return self.agent_dir / "schemas"

    @property
    def templates_dir(self) -> Path:
        return self.agent_dir / "templates"

    @property
    def state_dir(self) -> Path:
        return self.agent_dir / "state"

    @property
    def adapters_dir(self) -> Path:
        return self.agent_dir / "adapters"

    @property
    def research_dir(self) -> Path:
        return self.root / "research"

    @property
    def memory_dir(self) -> Path:
        return self.research_dir / "memory"

    @property
    def library_dir(self) -> Path:
        return self.root / "library"

    @property
    def library_papers_dir(self) -> Path:
        return self.library_dir / "papers"

    @property
    def library_books_dir(self) -> Path:
        return self.library_dir / "books"

    @property
    def library_articles_dir(self) -> Path:
        return self.library_dir / "articles"

    @property
    def library_datasets_dir(self) -> Path:
        return self.library_dir / "datasets"

    @property
    def literature_dir(self) -> Path:
        return self.root / "literature"

    @property
    def searches_dir(self) -> Path:
        return self.literature_dir / "searches"

    @property
    def references_dir(self) -> Path:
        return self.literature_dir / "references"

    @property
    def synthesis_dir(self) -> Path:
        return self.literature_dir / "synthesis"

    @property
    def experiments_dir(self) -> Path:
        return self.root / "experiments"

    @property
    def paper_projects_dir(self) -> Path:
        """Top-level `papers/` — LaTeX academic paper projects (VS013).

        Distinct from `library/papers/` (imported PDFs, VS004).
        """
        return self.root / "papers"

    @property
    def graph_dir(self) -> Path:
        return self.root / "graph"

    @property
    def vault_dir(self) -> Path:
        return self.root / "vault"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def cache_dir(self) -> Path:
        return self.root / ".cache"

    @property
    def venues_dir(self) -> Path:
        """Venue registry (VS013) — optional, lab-specific, created on
        demand rather than by `init` (unlike the always-present
        canonical directories in `LAB_SUBDIRS`)."""
        return self.root / "venues"
