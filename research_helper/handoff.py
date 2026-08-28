"""Cross-agent handoff (VS015, `fundactional.md` §16-17).

One `HandoffRecord` renders both `handoff.md` (human-readable) and
`handoff.json` (machine-readable) — single source, so they never diverge
on the facts they both represent (constitution Principle II).
"""
from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from research_helper.lab import LabPaths
from research_helper.tasks import load_active_task

# (markdown section title, field name) — fundactional.md §16 order,
# unioned with §17's JSON fields per this slice's Design note.
SECTIONS: list[tuple[str, str]] = [
    ("Objective", "objective"),
    ("Current Task", "task"),
    ("What Was Done", "what_was_done"),
    ("Evidence Collected", "evidence"),
    ("Files Changed", "files_changed"),
    ("Commands Executed", "commands"),
    ("Decisions", "decisions"),
    ("Assumptions", "assumptions"),
    ("Open Questions", "open_questions"),
    ("Known Problems", "known_problems"),
    ("Suggested Next Steps", "next_actions"),
    ("Reproduction Commands", "reproduction_commands"),
]


class HandoffRecord(BaseModel):
    session: str
    previous_agent: str
    task: str = ""
    objective: str | None = None
    status: str = "in-progress"
    what_was_done: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    known_problems: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    reproduction_commands: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


def render_handoff_md(record: HandoffRecord) -> str:
    lines = ["# Research Handoff", ""]
    for title, field in SECTIONS:
        value = getattr(record, field)
        if isinstance(value, list):
            body = "\n".join(f"- {item}" for item in value) if value else "-"
        else:
            body = value or "-"
        lines += [f"## {title}", "", body, ""]
    return "\n".join(lines).rstrip() + "\n"


def create_handoff(
    paths: LabPaths,
    *,
    agent: str,
    status: str = "in-progress",
    what_was_done: list[str] | None = None,
    evidence: list[str] | None = None,
    files_changed: list[str] | None = None,
    commands: list[str] | None = None,
    decisions: list[str] | None = None,
    assumptions: list[str] | None = None,
    open_questions: list[str] | None = None,
    known_problems: list[str] | None = None,
    next_actions: list[str] | None = None,
    reproduction_commands: list[str] | None = None,
    artifacts: list[str] | None = None,
) -> HandoffRecord:
    """FR-002, FR-003: pulls task/objective from VS002, writes both files."""
    task = load_active_task(paths)
    record = HandoffRecord(
        session=str(uuid4()),
        previous_agent=agent,
        task=task.id if task else "",
        objective=task.objective if task else None,
        status=status,
        what_was_done=what_was_done or [],
        evidence=evidence or [],
        files_changed=files_changed or [],
        commands=commands or [],
        decisions=decisions or [],
        assumptions=assumptions or [],
        open_questions=open_questions or [],
        known_problems=known_problems or [],
        next_actions=next_actions or [],
        reproduction_commands=reproduction_commands or [],
        artifacts=artifacts or [],
    )
    paths.state_dir.mkdir(parents=True, exist_ok=True)
    (paths.state_dir / "handoff.json").write_text(record.model_dump_json(indent=2), encoding="utf-8")
    (paths.state_dir / "handoff.md").write_text(render_handoff_md(record), encoding="utf-8")
    return record


def resume(paths: LabPaths) -> HandoffRecord | None:
    """FR-004: reconstruct the latest handoff purely from disk."""
    path = paths.state_dir / "handoff.json"
    if not path.is_file():
        return None
    return HandoffRecord.model_validate_json(path.read_text(encoding="utf-8"))
