import json

import pytest

from research_helper import lab, papers


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


@pytest.fixture
def fixture_pdf(tmp_path):
    path = tmp_path / "source.pdf"
    path.write_bytes(b"%PDF-1.4 fake content for testing\n")
    return path


def test_import_with_doi(lab_paths, fixture_pdf):
    paper_dir = papers.import_paper(lab_paths, fixture_pdf, doi="10.1145/1234567")

    assert paper_dir.name == "10.1145_1234567"
    assert (paper_dir / "paper.pdf").read_bytes() == fixture_pdf.read_bytes()
    manifest = json.loads((paper_dir / "manifest.json").read_text())
    assert manifest["doi"] == "10.1145/1234567"
    assert manifest["sha256"] == papers.sha256_of(fixture_pdf)


def test_import_without_doi_hash_fallback(lab_paths, fixture_pdf):
    paper_dir = papers.import_paper(lab_paths, fixture_pdf)

    assert paper_dir.name.startswith("paper-")
    metadata = json.loads((paper_dir / "metadata.json").read_text())
    assert metadata["doi"] is None


def test_reimport_is_idempotent(lab_paths, fixture_pdf):
    first = papers.import_paper(lab_paths, fixture_pdf, doi="10.1/x")
    manifest_before = (first / "manifest.json").read_text()

    second = papers.import_paper(lab_paths, fixture_pdf, doi="10.1/x")

    assert second == first
    assert len(list(lab_paths.library_papers_dir.iterdir())) == 1
    assert (first / "manifest.json").read_text() == manifest_before


def test_metadata_stub_never_fabricates_title(lab_paths, fixture_pdf):
    paper_dir = papers.import_paper(lab_paths, fixture_pdf, doi="10.1/y")
    metadata = json.loads((paper_dir / "metadata.json").read_text())
    assert metadata["title"] is None
