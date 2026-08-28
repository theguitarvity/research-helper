import pytest

from research_helper import lab, tasks
from research_helper.handoff import SECTIONS, create_handoff, resume


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def test_handoff_md_has_all_sections(lab_paths):
    create_handoff(lab_paths, agent="claude", what_was_done=["Searched literature"])

    content = (lab_paths.state_dir / "handoff.md").read_text()
    for title, _ in SECTIONS:
        assert f"## {title}" in content
    assert "Searched literature" in content


def test_handoff_json_roundtrip(lab_paths):
    record = create_handoff(
        lab_paths,
        agent="claude",
        open_questions=["Is dataset X still available?"],
        next_actions=["Resolve remaining references"],
    )

    reloaded = resume(lab_paths)

    assert reloaded == record


def test_create_then_resume_round_trip(lab_paths):
    tasks.create_task(lab_paths, type="review", objective="Evaluate caching", agent="claude")
    created = create_handoff(
        lab_paths,
        agent="claude",
        open_questions=["What about latency under load?"],
        next_actions=["Run the baseline experiment"],
    )

    # Simulate a fresh agent/process: no reference to `created` beyond this point.
    resumed = resume(lab.LabPaths.resolve(lab_paths.root))

    assert resumed.objective == "Evaluate caching"
    assert resumed.task == created.task
    assert resumed.open_questions == ["What about latency under load?"]
    assert resumed.next_actions == ["Run the baseline experiment"]


def test_resume_returns_none_when_absent(lab_paths):
    assert resume(lab_paths) is None
