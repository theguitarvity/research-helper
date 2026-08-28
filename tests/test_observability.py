import json

import pytest

from research_helper import lab
from research_helper.observability import log_event


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def test_log_event_rejects_arbitrary_kwargs(lab_paths):
    with pytest.raises(TypeError):
        log_event(lab_paths, api_key="secret-value")


def test_log_event_writes_jsonl_line(lab_paths):
    log_event(lab_paths, task="RT-001", agent="claude", tool="search", status="ok", tokens=120)

    log_path = lab_paths.logs_dir / "research-helper.jsonl"
    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["task"] == "RT-001"
    assert record["tokens"] == 120
    assert set(record) == {
        "timestamp", "task", "agent", "tool", "duration", "cache_hit", "tokens", "status", "artifacts",
    }


def test_log_event_appends(lab_paths):
    log_event(lab_paths, status="first")
    log_event(lab_paths, status="second")

    lines = (lab_paths.logs_dir / "research-helper.jsonl").read_text().splitlines()
    assert len(lines) == 2
