import yaml

from research_helper import lab
from research_helper.search import SearchQuery, SearchResult, dedup, run_search


class FakeClient:
    def __init__(self, name, results=None, error=None):
        self.name = name
        self._results = results or []
        self._error = error

    def search(self, query):
        if self._error:
            raise self._error
        return self._results


def make_result(**overrides):
    base = {"title": "A Great Paper", "authors": ["Ada Lovelace"], "year": 2024, "source": "test"}
    base.update(overrides)
    return SearchResult(**base)


def test_dedup_by_doi():
    a = make_result(doi="10.1/x", source="s1")
    b = make_result(title="A different title", doi="10.1/x", source="s2")
    assert dedup([a, b]) == [a]


def test_dedup_by_title_then_authors_year():
    a = make_result(title="Same Title Here", source="s1")
    b = make_result(title="same   title here", source="s2")
    assert len(dedup([a, b])) == 1


def test_no_dedup_across_unrelated_results():
    a = make_result(title="One", doi="10.1/one")
    b = make_result(title="Two", doi="10.1/two")
    assert len(dedup([a, b])) == 2


def test_run_search_writes_full_manifest(tmp_path):
    lab.scaffold(tmp_path)
    paths = lab.LabPaths.resolve(tmp_path)
    client = FakeClient("fake", results=[make_result(doi="10.1/x")])

    results = run_search(paths, SearchQuery(query="harness engineering"), [client])

    assert len(results) == 1
    manifest_dirs = list(paths.searches_dir.glob("*"))
    assert len(manifest_dirs) == 1
    manifest = manifest_dirs[0]
    for name in ("query.yaml", "raw-results.json", "normalized.json", "selected.json", "README.md"):
        assert (manifest / name).is_file()


def test_run_search_survives_one_client_failure(tmp_path):
    lab.scaffold(tmp_path)
    paths = lab.LabPaths.resolve(tmp_path)
    ok_client = FakeClient("ok", results=[make_result(doi="10.1/x")])
    bad_client = FakeClient("bad", error=RuntimeError("network down"))

    results = run_search(paths, SearchQuery(query="q"), [ok_client, bad_client])

    assert len(results) == 1
    manifest_dir = next(paths.searches_dir.glob("*"))
    readme = (manifest_dir / "README.md").read_text()
    assert "bad" in readme
    assert "network down" in readme


def test_query_yaml_roundtrip(tmp_path):
    lab.scaffold(tmp_path)
    paths = lab.LabPaths.resolve(tmp_path)
    query = SearchQuery(query="agentic software engineering", date_from=2024, date_to=2026)
    run_search(paths, query, [FakeClient("fake")])

    manifest_dir = next(paths.searches_dir.glob("*"))
    saved = yaml.safe_load((manifest_dir / "query.yaml").read_text())
    reloaded = SearchQuery(**{k: v for k, v in saved.items() if k != "executed_at"})
    assert reloaded == query
    assert "executed_at" in saved
