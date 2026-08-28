import pytest

from research_helper import lab
from research_helper.acquisition import acquire_references
from research_helper.references import ResolvedReference


class FakeDownloader:
    def __init__(self, content=b"%PDF-fake"):
        self.content = content
        self.call_count = 0
        self.urls = []

    def fetch(self, url):
        self.call_count += 1
        self.urls.append(url)
        return self.content


@pytest.fixture
def setup(lab_dir):
    lab.scaffold(lab_dir)
    paths = lab.LabPaths.resolve(lab_dir)
    paper_dir = paths.library_papers_dir / "paper-x"
    paper_dir.mkdir(parents=True)
    return paths, paper_dir


def test_oa_reference_downloaded(setup):
    paths, paper_dir = setup
    ref = ResolvedReference(
        raw_text="[1]", state="VERIFIED", pdf_url="https://oa.example/x.pdf", open_access=True
    )
    downloader = FakeDownloader()

    updated = acquire_references(paths, paper_dir, [ref], downloader)

    assert updated[0].acquisition_state == "DOWNLOADED"
    assert (paper_dir / updated[0].local_path).is_file()
    assert downloader.call_count == 1


def test_confirmed_non_oa_is_paywalled(setup):
    paths, paper_dir = setup
    ref = ResolvedReference(raw_text="[1]", state="RESOLVED", open_access=False)
    downloader = FakeDownloader()

    updated = acquire_references(paths, paper_dir, [ref], downloader)

    assert updated[0].acquisition_state == "PAYWALLED"
    assert downloader.call_count == 0
    assert not (paper_dir / "references" / "papers").exists()


def test_unconfirmed_is_metadata_only(setup):
    paths, paper_dir = setup
    ref = ResolvedReference(raw_text="[1]", state="UNAVAILABLE")
    downloader = FakeDownloader()

    updated = acquire_references(paths, paper_dir, [ref], downloader)

    assert updated[0].acquisition_state == "METADATA_ONLY"
    assert downloader.call_count == 0
    # still present in the resolved set, never dropped
    assert len(updated) == 1


def test_cache_avoids_second_fetch_call(setup):
    paths, paper_dir = setup
    ref = ResolvedReference(
        raw_text="[1]", state="VERIFIED", pdf_url="https://oa.example/x.pdf", open_access=True
    )
    downloader = FakeDownloader()

    acquire_references(paths, paper_dir, [ref], downloader)
    acquire_references(paths, paper_dir, [ref], downloader)

    assert downloader.call_count == 1
