import json

import pytest
import yaml

from research_helper import lab
from research_helper.validate import validate


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def test_clean_lab_has_zero_issues(lab_paths):
    assert validate(lab_paths) == []


def test_all_gates_flagged_on_broken_fixtures(lab_paths):
    papers_dir = lab_paths.library_papers_dir

    # 1. schema: malformed reference entry (raw_text missing)
    p1 = papers_dir / "p1"
    p1.mkdir(parents=True)
    (p1 / "references.normalized.json").write_text(json.dumps([{"doi": "10.1/x"}]))

    # 2. missing_provenance: no manifest.json at all
    p2 = papers_dir / "p2"
    p2.mkdir(parents=True)

    # 3. invalid_manifest: manifest.json missing required fields
    p3 = papers_dir / "p3"
    p3.mkdir(parents=True)
    (p3 / "manifest.json").write_text(json.dumps({"doi": "10.1/p3"}))

    # 4. duplicate_doi: two papers sharing a DOI
    p4 = papers_dir / "p4"
    p4.mkdir(parents=True)
    (p4 / "manifest.json").write_text(
        json.dumps({"source": "x", "retrieved_at": "now", "sha256": "a" * 64, "doi": "10.1/dup"})
    )
    p5 = papers_dir / "p5"
    p5.mkdir(parents=True)
    (p5 / "manifest.json").write_text(
        json.dumps({"source": "x", "retrieved_at": "now", "sha256": "b" * 64, "doi": "10.1/dup"})
    )

    # 5. broken_wikilink
    vault_papers = lab_paths.vault_dir / "Papers"
    vault_papers.mkdir(parents=True)
    (vault_papers / "orphan.md").write_text("See [[Nonexistent Title]] for details.\n")

    # 6. invalid_bibtex: unbalanced braces
    p6 = papers_dir / "p6"
    p6.mkdir(parents=True)
    (p6 / "references.bib").write_text("@article{x, title = {Unbalanced}\n")

    # 7. broken_latex: \input references a missing section file
    project_dir = lab_paths.paper_projects_dir / "proj1"
    (project_dir / "sections").mkdir(parents=True)
    (project_dir / "main.tex").write_text("\\input{sections/missing}\n")

    # 8. missing_experiment_metadata
    (lab_paths.experiments_dir / "exp1").mkdir(parents=True)

    # 9. invalid_handoff
    (lab_paths.state_dir / "handoff.json").write_text(json.dumps({"status": "bad"}))

    issues = validate(lab_paths)
    gates_found = {issue.gate for issue in issues}

    assert gates_found == {
        "schema",
        "missing_provenance",
        "invalid_manifest",
        "duplicate_doi",
        "broken_wikilink",
        "invalid_bibtex",
        "broken_latex",
        "missing_experiment_metadata",
        "invalid_handoff",
    }


def test_experiment_with_valid_manifest_is_not_flagged(lab_paths):
    exp_dir = lab_paths.experiments_dir / "exp-ok"
    exp_dir.mkdir(parents=True)
    (exp_dir / "manifest.yaml").write_text(yaml.safe_dump({"experiment": {"id": "EXP-001"}}))

    issues = validate(lab_paths)

    assert not any(i.gate == "missing_experiment_metadata" for i in issues)
