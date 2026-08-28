#!/usr/bin/env python3
"""Cross-platform bootstrap for research-helper (VS017,
`globalization.md` §61.3, §78).

Holds all real detection/setup logic. `bootstrap.sh` and `bootstrap.ps1`
are thin wrappers that only invoke this file — no logic is duplicated
per OS (§78 "One Core" design principle).
"""
from __future__ import annotations

import shutil
import subprocess
import sys


def _check(name: str, found: bool) -> None:
    print(f"  {name} ............. {'OK' if found else 'MISSING'}")


def main() -> int:
    print("research-helper bootstrap")
    print()
    print("Checking required tools:")
    _check("Python (>=3.12)", sys.version_info >= (3, 12))
    _check("uv", shutil.which("uv") is not None)
    _check("git", shutil.which("git") is not None)

    if shutil.which("uv") is None:
        print()
        print("uv not found. Install it from https://docs.astral.sh/uv/ and re-run.")
        return 1

    print()
    print("Installing dependencies with `uv sync --extra dev`...")
    result = subprocess.run(["uv", "sync", "--extra", "dev"], check=False)
    if result.returncode != 0:
        return result.returncode

    print()
    print("Bootstrap complete. Try: uv run research-helper doctor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
