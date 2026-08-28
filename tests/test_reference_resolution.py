import pytest

from research_helper import lab
from research_helper.references import RawReference, resolve_references
from research_helper.search import SearchResult


class FakeClient:
    def __init__(self, name, results=None, error=None):
        self.name = name
        self._results = results or []
        self._error = error

    def search(self, query):
        if self._error:
            raise self._error
        return self._results


def result(**overrides):
    base = {"title": "A Great Paper On Caching", "authors": ["Ada Lovelace"], "year": 2020, "source": "test"}
    base.update(overrides)
    return SearchResult(**base)


@pytest.fixture
def paper_dir(lab_dir):
    lab.scaffold(lab_dir)
    paths = lab.LabPaths.resolve(lab_dir)
    d = paths.library_papers_dir / "paper-x"
    d.mkdir(parents=True)
    return d


def test_exact_doi_match_is_verified(paper_dir):
    ref = RawReference(raw_text="[1] Smith, J. A Great Paper On Caching. 2020.", doi="10.1/x")
    client = FakeClient("s1", results=[result(doi="10.1/x")])

    resolved = resolve_references(paper_dir, [ref], [client])

    assert resolved[0].state == "VERIFIED"
    assert resolved[0].title == "A Great Paper On Caching"
    assert (paper_dir / "references.resolved.json").is_file()


def test_no_candidates_is_unavailable(paper_dir):
    ref = RawReference(raw_text="[1] Totally Unknown Paper. 2020.")
    client = FakeClient("s1", results=[])

    resolved = resolve_references(paper_dir, [ref], [client])

    assert resolved[0].state == "UNAVAILABLE"


def test_year_mismatch_flagged(paper_dir):
    ref = RawReference(
        raw_text="[1] Smith, J. A Great Paper On Caching. 2021.", doi="10.1/x"
    )
    client = FakeClient("s1", results=[result(doi="10.1/x", year=2020)])

    resolved = resolve_references(paper_dir, [ref], [client])

    assert resolved[0].state == "VERIFIED"
    assert len(resolved[0].consistency_flags) == 1
    assert "cited=2021" in resolved[0].consistency_flags[0]
    assert "resolved=2020" in resolved[0].consistency_flags[0]


def test_ambiguous_on_tied_candidates(paper_dir):
    ref = RawReference(raw_text="[1] A Great Paper On Caching Systems. 2020.")
    client = FakeClient(
        "s1",
        results=[
            result(title="A Great Paper On Caching Systems And More", doi="10.1/a"),
            result(title="A Great Paper On Caching Systems Also", doi="10.1/b"),
        ],
    )

    resolved = resolve_references(paper_dir, [ref], [client])

    assert resolved[0].state == "AMBIGUOUS"


def test_bibtex_written_for_resolved_and_unavailable(paper_dir):
    refs = [
        RawReference(raw_text="[1] Smith, J. A Great Paper On Caching. 2020.", doi="10.1/x"),
        RawReference(raw_text="[2] Totally Unknown Paper. 2020."),
    ]
    client = FakeClient("s1", results=[result(doi="10.1/x")])

    resolve_references(paper_dir, refs, [client])

    bibtex = (paper_dir / "references.bib").read_text()
    assert "@article{" in bibtex
    assert "A Great Paper On Caching" in bibtex
    assert "% UNAVAILABLE: [2] Totally Unknown Paper. 2020." in bibtex


def test_client_failure_does_not_abort_resolution(paper_dir):
    ref = RawReference(raw_text="[1] Smith, J. A Great Paper On Caching. 2020.", doi="10.1/x")
    ok_client = FakeClient("ok", results=[result(doi="10.1/x")])
    bad_client = FakeClient("bad", error=RuntimeError("down"))

    resolved = resolve_references(paper_dir, [ref], [ok_client, bad_client])

    assert resolved[0].state == "VERIFIED"
