import json

import pytest
import yaml

from research_helper import lab
from research_helper.paper_project import SECTION_NAMES, init_paper_project, load_venue


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def test_generic_venue_works_out_of_the_box(lab_paths):
    project_dir = init_paper_project(lab_paths, venue="generic", name="my-paper")

    assert (project_dir / "main.tex").is_file()
    venue_json = json.loads((project_dir / "venue.json").read_text())
    assert venue_json["name"] == "generic"
    assert venue_json["requirements"] == {}


def test_unregistered_venue_raises_with_expected_path(lab_paths):
    with pytest.raises(FileNotFoundError, match="venues/wop.yaml"):
        init_paper_project(lab_paths, venue="wop", name="my-paper")


def test_registered_venue_pinned_verbatim(lab_paths):
    lab_paths.venues_dir.mkdir(parents=True)
    (lab_paths.venues_dir / "acm.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "ACM",
                "template_source": "https://www.acm.org/publications/proceedings-template",
                "template_version": "2024.1",
                "requirements": {"pages": 12, "language": "en"},
                "assumptions": [],
            }
        )
    )

    project_dir = init_paper_project(lab_paths, venue="acm", name="my-paper")

    venue_json = json.loads((project_dir / "venue.json").read_text())
    assert venue_json["requirements"] == {"pages": 12, "language": "en"}
    assert venue_json["template_version"] == "2024.1"


def test_structure_matches_section_19(lab_paths):
    project_dir = init_paper_project(lab_paths, venue="generic", name="my-paper")

    for filename in ("main.tex", "references.bib", "Makefile", "README.md", "venue.json"):
        assert (project_dir / filename).is_file()
    for section in SECTION_NAMES:
        assert (project_dir / "sections" / f"{section}.tex").is_file()
    for subdir in ("figures", "tables", "assets"):
        assert (project_dir / subdir).is_dir()


def test_reinit_is_idempotent(lab_paths):
    first = init_paper_project(lab_paths, venue="generic", name="my-paper")
    before = (first / "main.tex").read_text()

    init_paper_project(lab_paths, venue="generic", name="my-paper")
    after = (first / "main.tex").read_text()

    assert before == after


def test_load_venue_generic_fallback(lab_paths):
    venue = load_venue(lab_paths, "generic")
    assert venue["name"] == "generic"
    assert venue["assumptions"]
