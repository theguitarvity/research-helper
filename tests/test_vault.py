import json

import pytest

from research_helper import lab, tasks
from research_helper.synthesis import NOT_DEFINED
from research_helper.vault import sync_vault, write_current_context


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def make_paper(lab_paths, identifier, doi=None, title=None, resolved_refs=None):
    paper_dir = lab_paths.library_papers_dir / identifier
    paper_dir.mkdir(parents=True)
    (paper_dir / "manifest.json").write_text(json.dumps({"doi": doi}))
    (paper_dir / "metadata.json").write_text(json.dumps({"doi": doi, "title": title}))
    if resolved_refs is not None:
        (paper_dir / "references.resolved.json").write_text(json.dumps(resolved_refs))
    return paper_dir


def test_wikilink_to_imported_paper(lab_paths):
    make_paper(lab_paths, "paper-b", doi="10.1/b", title="Paper B Title")
    make_paper(
        lab_paths,
        "paper-a",
        doi="10.1/a",
        title="Paper A Title",
        resolved_refs=[{"raw_text": "[1]", "doi": "10.1/b", "state": "VERIFIED"}],
    )

    sync_vault(lab_paths)

    note_a = (lab_paths.vault_dir / "Papers" / "paper-a.md").read_text()
    assert "[[Paper B Title]]" in note_a


def test_plain_text_for_external_reference(lab_paths):
    make_paper(
        lab_paths,
        "paper-a",
        doi="10.1/a",
        title="Paper A Title",
        resolved_refs=[{"raw_text": "[1]", "doi": "10.1/z", "title": "External Paper", "state": "VERIFIED"}],
    )

    sync_vault(lab_paths)

    note_a = (lab_paths.vault_dir / "Papers" / "paper-a.md").read_text()
    assert "[[External Paper]]" not in note_a
    assert "External Paper (external, doi: 10.1/z)" in note_a


def test_sync_vault_idempotent(lab_paths):
    make_paper(lab_paths, "paper-a", doi="10.1/a", title="Paper A Title")

    sync_vault(lab_paths)
    first = (lab_paths.vault_dir / "Papers" / "paper-a.md").read_bytes()
    sync_vault(lab_paths)
    second = (lab_paths.vault_dir / "Papers" / "paper-a.md").read_bytes()

    assert first == second


def test_current_context_has_all_sections(lab_paths):
    tasks.create_task(lab_paths, type="review", objective="Investigate caching", agent="claude")

    dest = write_current_context(lab_paths)
    content = dest.read_text()

    for heading in (
        "What research is being done",
        "What problem is being investigated",
        "Hypotheses",
        "Important papers",
        "Active experiments",
        "Open questions",
        "Next steps",
    ):
        assert f"## {heading}" in content
    assert "Investigate caching" in content
    assert NOT_DEFINED in content


def test_summary_uses_synthesis_when_present(lab_paths):
    make_paper(lab_paths, "paper-a", doi="10.1/a", title="Paper A Title")
    synth_dir = lab_paths.synthesis_dir / "individual"
    synth_dir.mkdir(parents=True)
    (synth_dir / "paper-a.md").write_text("# Paper\n\n## Metadata\n\nCustom summary text.\n")

    sync_vault(lab_paths)

    note_a = (lab_paths.vault_dir / "Papers" / "paper-a.md").read_text()
    assert "Custom summary text." in note_a
