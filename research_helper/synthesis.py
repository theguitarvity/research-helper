"""Structured paper synthesis persistence (VS008, `fundactional.md` §11).

Deterministic scaffolding only — see spec.md's Architecture note: this
module never reads a PDF or calls an LLM; it renders/persists section
content the agent has already produced by reading the paper
(constitution Principle III: script what's deterministic, the agent
reasons).
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from research_helper.lab import LabPaths

NOT_DEFINED = "Not defined by current context."

# fundactional.md §11, in order.
SECTION_TITLES: list[tuple[str, str]] = [
    ("metadata", "Metadata"),
    ("research_problem", "Research Problem"),
    ("research_question", "Research Question"),
    ("hypothesis", "Hypothesis"),
    ("methodology", "Methodology"),
    ("dataset", "Dataset"),
    ("experiment", "Experiment"),
    ("results", "Results"),
    ("contributions", "Contributions"),
    ("limitations", "Limitations"),
    ("threats_to_validity", "Threats to Validity"),
    ("related_work", "Related Work"),
    ("important_claims", "Important Claims"),
    ("evidence", "Evidence"),
    ("relevance_to_current_research", "Relevance to Current Research"),
    ("questions_raised", "Questions Raised"),
    ("researchers_notes", "Researcher's Notes"),
]


class PaperSynthesis(BaseModel):
    metadata: str | None = None
    research_problem: str | None = None
    research_question: str | None = None
    hypothesis: str | None = None
    methodology: str | None = None
    dataset: str | None = None
    experiment: str | None = None
    results: str | None = None
    contributions: str | None = None
    limitations: str | None = None
    threats_to_validity: str | None = None
    related_work: str | None = None
    important_claims: str | None = None
    evidence: str | None = None
    relevance_to_current_research: str | None = None
    questions_raised: str | None = None
    researchers_notes: str | None = None


def render_synthesis(synthesis: PaperSynthesis) -> str:
    """FR-002: every §11 section, in order; unset -> NOT_DEFINED."""
    lines = ["# Paper", ""]
    for field, title in SECTION_TITLES:
        content = getattr(synthesis, field) or NOT_DEFINED
        lines += [f"## {title}", "", content, ""]
    return "\n".join(lines).rstrip() + "\n"


def write_individual_synthesis(paths: LabPaths, paper_id: str, synthesis: PaperSynthesis) -> Path:
    out_dir = paths.synthesis_dir / "individual"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{paper_id}.md"
    dest.write_text(render_synthesis(synthesis), encoding="utf-8")
    return dest


def write_comparative_synthesis(
    paths: LabPaths,
    *,
    comparison: str | None = None,
    disagreements: str | None = None,
    common_findings: str | None = None,
    research_gaps: str | None = None,
) -> dict[str, Path]:
    """FR-004: always writes all four cross-paper artifacts."""
    sections = {
        "comparison.md": comparison,
        "disagreements.md": disagreements,
        "common-findings.md": common_findings,
        "research-gaps.md": research_gaps,
    }
    written: dict[str, Path] = {}
    for filename, content in sections.items():
        dest = paths.synthesis_dir / filename
        dest.write_text((content or NOT_DEFINED) + "\n", encoding="utf-8")
        written[filename] = dest
    return written
