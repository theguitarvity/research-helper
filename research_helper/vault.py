"""Obsidian vault generation + research memory checkpoint (VS011,
`fundactional.md` §14-15).

Every link is derived from `research_helper.graph.build_graph`'s already
-deterministic output — never hand-written by an LLM (§14, explicit).
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from research_helper.graph import build_graph
from research_helper.lab import LabPaths
from research_helper.synthesis import NOT_DEFINED
from research_helper.tasks import load_active_task


def _imported_paper_ids(paths: LabPaths) -> set[str]:
    if not paths.library_papers_dir.is_dir():
        return set()
    return {p.name for p in paths.library_papers_dir.iterdir() if p.is_dir()}


def sync_vault(paths: LabPaths) -> dict[str, Path]:
    """FR-001..FR-004: script-generated vault, links only from the graph."""
    graph = build_graph(paths)
    nodes_by_id = {n.id: n for n in graph.nodes}
    imported_ids = _imported_paper_ids(paths)

    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        if edge.type == "CITES":
            outgoing[edge.source].append(edge.target)

    papers_dir = paths.vault_dir / "Papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, Path] = {}
    for pid in sorted(imported_ids):
        node = nodes_by_id.get(pid)
        title = (node.properties.get("title") if node else None) or pid
        doi = node.properties.get("doi") if node else None

        synthesis_path = paths.synthesis_dir / "individual" / f"{pid}.md"
        summary = synthesis_path.read_text(encoding="utf-8").strip() if synthesis_path.is_file() else NOT_DEFINED

        reference_lines = []
        for target in sorted(set(outgoing.get(pid, []))):
            target_node = nodes_by_id[target]
            target_title = target_node.properties.get("title") or target
            if target in imported_ids:
                reference_lines.append(f"[[{target_title}]]")
            else:
                target_doi = target_node.properties.get("doi", "unknown")
                reference_lines.append(f"{target_title} (external, doi: {target_doi})")

        frontmatter_lines = ["---", "type: paper", "status: imported"]
        if doi:
            frontmatter_lines.append(f"doi: {doi}")
        frontmatter_lines.append("---")

        body = [
            *frontmatter_lines,
            "",
            f"# {title}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## References",
            "",
            *([f"- {line}" for line in reference_lines] if reference_lines else [NOT_DEFINED]),
        ]
        dest = papers_dir / f"{pid}.md"
        dest.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
        written[pid] = dest

    return written


def write_current_context(paths: LabPaths) -> Path:
    """FR-005: one section per §15 bullet, real data or NOT_DEFINED."""
    task = load_active_task(paths)
    imported_ids = sorted(_imported_paper_ids(paths))

    objective = task.objective if task else NOT_DEFINED
    important_papers = "\n".join(f"- {pid}" for pid in imported_ids) if imported_ids else NOT_DEFINED
    next_steps = "\n".join(f"- {s}" for s in task.steps) if task and task.steps else NOT_DEFINED

    sections = [
        ("What research is being done", objective),
        ("What problem is being investigated", objective),
        ("Hypotheses", NOT_DEFINED),
        ("Important papers", important_papers),
        ("Active experiments", NOT_DEFINED),
        ("Open questions", NOT_DEFINED),
        ("Next steps", next_steps),
    ]

    lines = ["# Current Context", ""]
    for title, content in sections:
        lines += [f"## {title}", "", content, ""]

    dest = paths.memory_dir / "current-context.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return dest
