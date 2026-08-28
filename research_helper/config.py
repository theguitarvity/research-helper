"""Global configuration path resolution (VS017, `globalization.md` §64).

`system` is injectable so all branches are testable without mocking
global interpreter state (`platform.system()`), per this slice's spec.
"""
from __future__ import annotations

import os
import platform
from pathlib import Path

APP_NAME = "research-helper"


def global_config_dir(system: str | None = None) -> Path:
    """FR-005: §64's OS convention mapping."""
    system = system or platform.system()

    if system == "Windows":
        base = os.environ.get("APPDATA")
        return Path(base) / APP_NAME if base else Path.home() / "AppData" / "Roaming" / APP_NAME

    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME

    # Linux and Android/Termux both use the XDG convention (§64).
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base_dir = Path(xdg) if xdg else Path.home() / ".config"
    return base_dir / APP_NAME
