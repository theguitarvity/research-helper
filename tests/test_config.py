from pathlib import Path

from research_helper.config import global_config_dir


def test_global_config_dir_windows(monkeypatch):
    monkeypatch.setenv("APPDATA", "C:/Users/researcher/AppData/Roaming")
    assert global_config_dir("Windows") == Path("C:/Users/researcher/AppData/Roaming/research-helper")


def test_global_config_dir_macos():
    expected = Path.home() / "Library" / "Application Support" / "research-helper"
    assert global_config_dir("Darwin") == expected


def test_global_config_dir_linux_xdg(monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", "/home/researcher/.config")
    assert global_config_dir("Linux") == Path("/home/researcher/.config/research-helper")


def test_global_config_dir_linux_no_xdg(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    expected = Path.home() / ".config" / "research-helper"
    assert global_config_dir("Linux") == expected
