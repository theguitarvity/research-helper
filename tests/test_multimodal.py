import json

import pytest

from research_helper import lab
from research_helper.multimodal import (
    create_delegation_task,
    extract_images,
    record_figure_analysis,
)


class FakeImage:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class FakePage:
    def __init__(self, images):
        self.images = images


class FakeReader:
    def __init__(self, pages):
        self.pages = pages


@pytest.fixture
def paper_dir(lab_dir):
    lab.scaffold(lab_dir)
    paths = lab.LabPaths.resolve(lab_dir)
    d = paths.library_papers_dir / "paper-x"
    d.mkdir(parents=True)
    return d, paths


def test_extract_images_from_fake_reader(paper_dir):
    d, _ = paper_dir
    reader = FakeReader(
        pages=[
            FakePage([FakeImage("im0.png", b"\x89PNG-fake-1")]),
            FakePage([FakeImage("im1.jpeg", b"\xff\xd8-fake-2")]),
        ]
    )

    results = extract_images(d, reader=reader)

    assert len(results) == 2
    assert results[0].figure == "figure-001"
    assert results[0].page == 1
    assert results[1].page == 2
    assert (d / "figures" / "figure-001.png").read_bytes() == b"\x89PNG-fake-1"
    assert (d / "figures" / "figure-002.jpeg").read_bytes() == b"\xff\xd8-fake-2"
    for fid in ("figure-001", "figure-002"):
        metadata = json.loads((d / "figures" / f"{fid}.json").read_text())
        assert metadata["caption"] is None
        assert metadata["analysis_model"] is None
        assert (d / "figures" / f"{fid}.analysis.md").is_file()


def test_record_figure_analysis_updates_only_given_fields(paper_dir):
    d, _ = paper_dir
    reader = FakeReader(pages=[FakePage([FakeImage("im0.png", b"data")])])
    extract_images(d, reader=reader)

    updated = record_figure_analysis(
        d, "figure-001", caption="Figure 1: architecture diagram", analysis_model="claude-sonnet-5"
    )

    assert updated.caption == "Figure 1: architecture diagram"
    assert updated.analysis_model == "claude-sonnet-5"
    assert updated.page == 1  # untouched field preserved

    record_figure_analysis(d, "figure-001", analysis="This diagram shows X.")
    analysis_text = (d / "figures" / "figure-001.analysis.md").read_text()
    assert "This diagram shows X." in analysis_text
    reloaded = json.loads((d / "figures" / "figure-001.json").read_text())
    assert reloaded["caption"] == "Figure 1: architecture diagram"  # not clobbered


def test_create_delegation_task_writes_file(paper_dir):
    _, paths = paper_dir

    dest = create_delegation_task(
        paths, capability="multimodal-analysis", reason="Current agent has no vision support."
    )

    assert dest.is_file()
    record = json.loads(dest.read_text())
    assert record["state"] == "CAPABILITY_UNAVAILABLE"
    assert record["capability"] == "multimodal-analysis"
