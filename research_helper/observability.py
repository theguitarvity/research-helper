"""Structured observability logging (VS017, `fundactional.md` §40-41).

`log_event`'s signature is the fixed §40 field set with no `**kwargs` —
structurally, there is no parameter through which a secret-shaped key
could reach a log line.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime

from research_helper.lab import LabPaths


def log_event(
    paths: LabPaths,
    *,
    task: str | None = None,
    agent: str | None = None,
    tool: str | None = None,
    duration: float | None = None,
    cache_hit: bool | None = None,
    tokens: int | None = None,
    status: str | None = None,
    artifacts: list[str] | None = None,
) -> None:
    """FR-004: append one JSONL line with exactly the §40 fields."""
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "task": task,
        "agent": agent,
        "tool": tool,
        "duration": duration,
        "cache_hit": cache_hit,
        "tokens": tokens,
        "status": status,
        "artifacts": artifacts or [],
    }
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = paths.logs_dir / "research-helper.jsonl"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
