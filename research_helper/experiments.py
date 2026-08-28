"""Experiment scaffolding (VS012, `fundactional.md` §21-23)."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from research_helper.lab import LabPaths

EXPERIMENT_SUBDIRS: tuple[str, ...] = (
    "environment",
    "src",
    "scripts",
    "datasets",
    "raw",
    "results",
    "analysis",
    "figures",
    "logs",
)
EXPERIMENT_FILES: tuple[str, ...] = ("README.md", "hypothesis.md", "protocol.md")


def _next_experiment_id(paths: LabPaths) -> str:
    highest = 0
    if paths.experiments_dir.is_dir():
        for manifest_path in paths.experiments_dir.glob("*/manifest.yaml"):
            manifest = yaml.safe_load(manifest_path.read_text())
            exp_id = (manifest.get("experiment") or {}).get("id", "")
            try:
                highest = max(highest, int(exp_id.removeprefix("EXP-")))
            except ValueError:
                continue
    return f"EXP-{highest + 1:03d}"


def init_experiment(
    paths: LabPaths,
    name: str,
    *,
    title: str | None = None,
    research_question: str | None = None,
    hypothesis: str | None = None,
    independent: list[str] | None = None,
    dependent: list[str] | None = None,
    controlled: list[str] | None = None,
    dataset: str | None = None,
    environment: str | None = None,
    reproduction_command: str | None = None,
    llm: dict | None = None,
) -> Path:
    """FR-001..FR-005: scaffold §21 structure + §22 manifest."""
    exp_dir = paths.experiments_dir / name
    manifest_path = exp_dir / "manifest.yaml"
    if manifest_path.exists():
        return exp_dir

    exp_dir.mkdir(parents=True, exist_ok=True)
    for rel in EXPERIMENT_SUBDIRS:
        (exp_dir / rel).mkdir(parents=True, exist_ok=True)
    for filename in EXPERIMENT_FILES:
        (exp_dir / filename).touch()

    manifest: dict = {
        "experiment": {
            "id": _next_experiment_id(paths),
            "title": title or name,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "planned",
        },
        "research_question": research_question,
        "hypothesis": hypothesis,
        "variables": {
            "independent": independent or [],
            "dependent": dependent or [],
            "controlled": controlled or [],
        },
        "dataset": dataset,
        "environment": environment,
        "reproduction": {"command": reproduction_command},
        "outputs": [],
    }
    if llm:
        manifest["llm"] = llm

    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return exp_dir
