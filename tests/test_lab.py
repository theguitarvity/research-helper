import time

from research_helper import lab


def test_scaffold_creates_all_dirs(lab_dir):
    root = lab.scaffold(lab_dir)

    assert root == lab_dir
    for rel in lab.LAB_SUBDIRS:
        assert (root / rel).is_dir(), f"missing {rel}"
    assert (root / lab.MANIFEST_NAME).is_file()


def test_scaffold_idempotent_preserves_content(lab_dir):
    lab.scaffold(lab_dir)
    marker = lab_dir / "library" / "papers" / "marker.txt"
    marker.write_text("do not touch")
    manifest_mtime = (lab_dir / lab.MANIFEST_NAME).stat().st_mtime

    time.sleep(0.01)
    lab.scaffold(lab_dir)

    assert marker.read_text() == "do not touch"
    assert (lab_dir / lab.MANIFEST_NAME).stat().st_mtime == manifest_mtime


def test_scaffold_creates_missing_parents(tmp_path):
    nested = tmp_path / "a" / "b" / "c" / "lab"
    root = lab.scaffold(nested)
    assert root.is_dir()
    assert (root / lab.MANIFEST_NAME).is_file()


def test_no_absolute_or_backslash_paths_persisted(lab_dir):
    lab.scaffold(lab_dir)
    text = (lab_dir / lab.MANIFEST_NAME).read_text()
    assert str(lab_dir) not in text
    assert "\\" not in text


def test_resolve_lab_root_from_nested_cwd(lab_dir):
    lab.scaffold(lab_dir)
    nested = lab_dir / "library" / "papers"
    assert lab.resolve_lab_root(nested) == lab_dir


def test_resolve_lab_root_returns_none_outside_a_lab(tmp_path):
    assert lab.resolve_lab_root(tmp_path) is None


def test_scaffold_writes_agent_persona(lab_dir):
    lab.scaffold(lab_dir)
    agent_dir = lab_dir / ".agent" / "agents" / "research-helper"
    assert (agent_dir / "AGENT.md").is_file()
    assert (agent_dir / "README.md").is_file()


def test_lab_paths_resolve(lab_dir):
    lab.scaffold(lab_dir)
    paths = lab.LabPaths.resolve(lab_dir)
    assert paths.library_papers_dir == lab_dir / "library" / "papers"
    assert paths.paper_projects_dir == lab_dir / "papers"
    assert paths.skills_dir.is_dir()
