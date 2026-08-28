from typer.testing import CliRunner

from research_helper import lab
from research_helper.cli import app

runner = CliRunner()


def test_init_default_path_is_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / lab.MANIFEST_NAME).is_file()


def test_init_explicit_nested_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = "nested/does/not/exist/yet"
    result = runner.invoke(app, ["init", target])
    assert result.exit_code == 0
    assert (tmp_path / target / lab.MANIFEST_NAME).is_file()
