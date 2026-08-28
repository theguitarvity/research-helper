"""Research Task + session state (VS002).

Backs `.agent/state/{session,active-task,tasks/<id>}.json`. A Research
Task is agent-independent: any agent can create one, touch it, and any
other agent can reload it from disk (constitution Principle I/II).
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from research_helper.lab import LabPaths

TASK_ID_RE_PREFIX = "RT-"


class ResearchTask(BaseModel):
    id: str
    type: str
    objective: str
    inputs: list[str] = Field(default_factory=list)
    status: str = "planned"
    steps: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    agent_history: list[str] = Field(default_factory=list)


def _tasks_dir(paths: LabPaths) -> Path:
    d = paths.state_dir / "tasks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _active_task_path(paths: LabPaths) -> Path:
    return paths.state_dir / "active-task.json"


def _session_path(paths: LabPaths) -> Path:
    return paths.state_dir / "session.json"


def _next_task_id(paths: LabPaths) -> str:
    existing = _tasks_dir(paths).glob(f"{TASK_ID_RE_PREFIX}*.json")
    highest = 0
    for p in existing:
        try:
            highest = max(highest, int(p.stem.removeprefix(TASK_ID_RE_PREFIX)))
        except ValueError:
            continue
    return f"{TASK_ID_RE_PREFIX}{highest + 1:03d}"


def _write_task(paths: LabPaths, task: ResearchTask) -> None:
    (_tasks_dir(paths) / f"{task.id}.json").write_text(
        task.model_dump_json(indent=2), encoding="utf-8"
    )
    _active_task_path(paths).write_text(task.model_dump_json(indent=2), encoding="utf-8")


def create_task(
    paths: LabPaths,
    type: str,
    objective: str,
    inputs: list[str] | None = None,
    steps: list[str] | None = None,
    agent: str = "unknown",
) -> ResearchTask:
    task = ResearchTask(
        id=_next_task_id(paths),
        type=type,
        objective=objective,
        inputs=inputs or [],
        steps=steps or [],
        agent_history=[agent],
    )
    _write_task(paths, task)
    return task


def load_task(paths: LabPaths, task_id: str) -> ResearchTask | None:
    path = _tasks_dir(paths) / f"{task_id}.json"
    if not path.is_file():
        return None
    return ResearchTask.model_validate_json(path.read_text(encoding="utf-8"))


def load_active_task(paths: LabPaths) -> ResearchTask | None:
    path = _active_task_path(paths)
    if not path.is_file():
        return None
    return ResearchTask.model_validate_json(path.read_text(encoding="utf-8"))


def record_agent_touch(paths: LabPaths, agent: str) -> ResearchTask:
    task = load_active_task(paths)
    if task is None:
        raise LookupError("No active Research Task to record an agent touch against.")
    if not task.agent_history or task.agent_history[-1] != agent:
        task.agent_history.append(agent)
    _write_task(paths, task)
    return task


def start_session(paths: LabPaths, agent: str) -> dict:
    session = {
        "session_id": str(uuid4()),
        "started_at": datetime.now(UTC).isoformat(),
        "current_agent": agent,
    }
    _session_path(paths).write_text(json.dumps(session, indent=2), encoding="utf-8")
    return session
