import pytest

from research_helper import lab, tasks


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def test_create_and_reload_task(lab_paths):
    created = tasks.create_task(
        lab_paths,
        type="literature-review",
        objective="Evaluate semantic caching for RAG",
        steps=["search-literature", "synthesize"],
        agent="claude",
    )
    reloaded = tasks.load_active_task(lab_paths)
    assert reloaded == created
    assert reloaded.id.startswith("RT-")


def test_record_agent_touch_appends_history(lab_paths):
    tasks.create_task(lab_paths, type="review", objective="x", agent="claude")
    tasks.record_agent_touch(lab_paths, "codex")
    task = tasks.load_active_task(lab_paths)
    assert task.agent_history == ["claude", "codex"]


def test_record_agent_touch_dedupes_consecutive(lab_paths):
    tasks.create_task(lab_paths, type="review", objective="x", agent="claude")
    tasks.record_agent_touch(lab_paths, "claude")
    task = tasks.load_active_task(lab_paths)
    assert task.agent_history == ["claude"]


def test_load_active_task_none_when_absent(lab_paths):
    assert tasks.load_active_task(lab_paths) is None


def test_record_agent_touch_without_active_task_raises(lab_paths):
    with pytest.raises(LookupError):
        tasks.record_agent_touch(lab_paths, "codex")


def test_second_task_keeps_first_addressable(lab_paths):
    first = tasks.create_task(lab_paths, type="review", objective="first", agent="claude")
    second = tasks.create_task(lab_paths, type="review", objective="second", agent="claude")
    assert second.id != first.id
    assert tasks.load_task(lab_paths, first.id) == first
    assert tasks.load_active_task(lab_paths) == second


def test_start_session_writes_session_file(lab_paths):
    session = tasks.start_session(lab_paths, "gemini")
    assert (lab_paths.state_dir / "session.json").is_file()
    assert session["current_agent"] == "gemini"
