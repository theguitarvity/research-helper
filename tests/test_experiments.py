import pytest
import yaml

from research_helper import lab
from research_helper.experiments import EXPERIMENT_FILES, EXPERIMENT_SUBDIRS, init_experiment


@pytest.fixture
def lab_paths(lab_dir):
    lab.scaffold(lab_dir)
    return lab.LabPaths.resolve(lab_dir)


def test_init_creates_full_structure(lab_paths):
    exp_dir = init_experiment(lab_paths, "attention-cache")

    for rel in EXPERIMENT_SUBDIRS:
        assert (exp_dir / rel).is_dir()
    for filename in EXPERIMENT_FILES:
        assert (exp_dir / filename).is_file()
    assert (exp_dir / "manifest.yaml").is_file()


def test_manifest_roundtrip(lab_paths):
    exp_dir = init_experiment(
        lab_paths,
        "semantic-cache",
        title="Semantic Cache Eval",
        research_question="Does semantic caching reduce cost?",
        hypothesis="Yes, by >30%",
        independent=["cache_strategy"],
        dependent=["latency"],
        dataset="ms-marco",
        reproduction_command="uv run experiments/semantic-cache/scripts/run.py",
    )

    manifest = yaml.safe_load((exp_dir / "manifest.yaml").read_text())

    assert manifest["experiment"]["title"] == "Semantic Cache Eval"
    assert manifest["research_question"] == "Does semantic caching reduce cost?"
    assert manifest["variables"]["independent"] == ["cache_strategy"]
    assert manifest["reproduction"]["command"] == (
        "uv run experiments/semantic-cache/scripts/run.py"
    )


def test_no_llm_section_when_not_supplied(lab_paths):
    exp_dir = init_experiment(lab_paths, "baseline")
    manifest = yaml.safe_load((exp_dir / "manifest.yaml").read_text())
    assert "llm" not in manifest


def test_llm_section_when_supplied(lab_paths):
    exp_dir = init_experiment(
        lab_paths, "llm-eval", llm={"provider": "anthropic", "model": "claude-sonnet-5"}
    )
    manifest = yaml.safe_load((exp_dir / "manifest.yaml").read_text())
    assert manifest["llm"]["provider"] == "anthropic"


def test_sequential_ids(lab_paths):
    first = init_experiment(lab_paths, "exp-a")
    second = init_experiment(lab_paths, "exp-b")

    first_manifest = yaml.safe_load((first / "manifest.yaml").read_text())
    second_manifest = yaml.safe_load((second / "manifest.yaml").read_text())

    assert first_manifest["experiment"]["id"] == "EXP-001"
    assert second_manifest["experiment"]["id"] == "EXP-002"


def test_reinit_is_idempotent(lab_paths):
    first_dir = init_experiment(lab_paths, "exp-a", title="Original")
    before = (first_dir / "manifest.yaml").read_text()

    init_experiment(lab_paths, "exp-a", title="Changed")
    after = (first_dir / "manifest.yaml").read_text()

    assert before == after
