import json

import pytest
from pdf_fixtures import make_pdf

from research_helper import lab
from research_helper.references import extract_doi, extract_references


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def make_paper_dir(lab_paths, identifier, lines):
    paper_dir = lab_paths.library_papers_dir / identifier
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "paper.pdf").write_bytes(make_pdf(lines))
    return paper_dir


def test_extract_bracket_numbered_references(lab_paths):
    paper_dir = make_paper_dir(
        lab_paths,
        "paper-a",
        [
            "Some Title",
            "References",
            "[1] Smith, J. A Great Paper. 2020.",
            "[2] Doe, A. Another Paper. 2019.",
            "[3] Lee, K. Third Paper. 2021.",
        ],
    )

    refs = extract_references(paper_dir)

    assert len(refs) == 3
    raw = json.loads((paper_dir / "references.raw.json").read_text())
    normalized = json.loads((paper_dir / "references.normalized.json").read_text())
    assert len(raw) == 3
    assert len(normalized) == 3
    assert all(r["state"] == "DISCOVERED" for r in normalized)


def test_extract_no_references_section(lab_paths):
    paper_dir = make_paper_dir(lab_paths, "paper-b", ["Just a title", "No references here."])

    refs = extract_references(paper_dir)

    assert refs == []
    assert json.loads((paper_dir / "references.raw.json").read_text()) == []


def test_extract_captures_embedded_doi(lab_paths):
    paper_dir = make_paper_dir(
        lab_paths,
        "paper-c",
        [
            "References",
            "[1] Smith, J. A Great Paper. 2020. doi:10.1145/1234567",
        ],
    )

    refs = extract_references(paper_dir)

    assert len(refs) == 1
    assert refs[0].doi == "10.1145/1234567"


def test_extract_plain_numbered_references(lab_paths):
    paper_dir = make_paper_dir(
        lab_paths,
        "paper-d",
        [
            "Bibliography",
            "1. Smith, J. A Great Paper. 2020.",
            "2. Doe, A. Another Paper. 2019.",
        ],
    )

    refs = extract_references(paper_dir)

    assert len(refs) == 2


def test_extract_doi_strips_trailing_punctuation():
    assert extract_doi("See doi:10.1145/abc.def).") == "10.1145/abc.def"
    assert extract_doi("no doi here") is None
