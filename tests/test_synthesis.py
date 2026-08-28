import pytest

from research_helper import lab
from research_helper.synthesis import (
    NOT_DEFINED,
    SECTION_TITLES,
    PaperSynthesis,
    render_synthesis,
    write_comparative_synthesis,
    write_individual_synthesis,
)


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def test_render_marks_unset_sections_not_defined():
    synthesis = PaperSynthesis(
        metadata="Title: X", results="We found Y.", researchers_notes="Interesting."
    )

    rendered = render_synthesis(synthesis)

    assert rendered.count(NOT_DEFINED) == len(SECTION_TITLES) - 3
    assert "Title: X" in rendered
    assert "We found Y." in rendered
    for _, title in SECTION_TITLES:
        assert f"## {title}" in rendered


def test_write_individual_synthesis_path(lab_paths):
    dest = write_individual_synthesis(lab_paths, "paper-a", PaperSynthesis())
    assert dest == lab_paths.synthesis_dir / "individual" / "paper-a.md"
    assert dest.is_file()


def test_comparative_synthesis_always_writes_four_files(lab_paths):
    written = write_comparative_synthesis(lab_paths, comparison="A vs B")

    assert set(written) == {
        "comparison.md",
        "disagreements.md",
        "common-findings.md",
        "research-gaps.md",
    }
    for path in written.values():
        assert path.is_file()
    assert "A vs B" in written["comparison.md"].read_text()
    assert NOT_DEFINED in written["disagreements.md"].read_text()
