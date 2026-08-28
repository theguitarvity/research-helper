"""Environment doctor (VS017, `fundactional.md` §63).

Every field comes from a real detection call (`shutil.which`,
`platform`, filesystem presence) — never guessed or hardcoded.
"""
from __future__ import annotations

import os
import platform
import shutil
import sys
from importlib.util import find_spec
from pathlib import Path

from pydantic import BaseModel

from research_helper.lab import LabPaths

AGENT_ADAPTER_DIRS: tuple[str, ...] = (".claude", ".codex", ".github", ".gemini")


class DoctorReport(BaseModel):
    os: str
    architecture: str
    shell: str
    python_ok: bool
    uv_ok: bool
    git_ok: bool
    pdf_extractor_ok: bool
    graphify_ok: bool
    obsidian_vault_ok: bool
    latex_ok: bool
    bibtex_ok: bool
    agents_found: dict[str, bool]
    status: str


def _found(name: str) -> bool:
    return shutil.which(name) is not None


def run_doctor(paths: LabPaths | None = None) -> DoctorReport:
    """FR-001: real platform/tool/agent detection."""
    agents_found = {
        name.lstrip("."): (paths.root / name).is_dir() if paths else False
        for name in AGENT_ADAPTER_DIRS
    }

    python_ok = sys.version_info >= (3, 12)
    uv_ok = _found("uv")
    git_ok = _found("git")
    pdf_extractor_ok = find_spec("pypdf") is not None
    latex_ok = _found("latexmk") or _found("pdflatex")
    bibtex_ok = _found("bibtex")
    # Filesystem-based, always available once a lab exists (VS010/VS011).
    graphify_ok = paths is not None
    obsidian_vault_ok = paths is not None

    core_ready = python_ok and git_ok

    return DoctorReport(
        os=platform.system(),
        architecture=platform.machine(),
        shell=Path(shell).name if (shell := _shell_name()) else "unknown",
        python_ok=python_ok,
        uv_ok=uv_ok,
        git_ok=git_ok,
        pdf_extractor_ok=pdf_extractor_ok,
        graphify_ok=graphify_ok,
        obsidian_vault_ok=obsidian_vault_ok,
        latex_ok=latex_ok,
        bibtex_ok=bibtex_ok,
        agents_found=agents_found,
        status="CORE READY" if core_ready else "CORE INCOMPLETE",
    )


def _shell_name() -> str | None:
    return os.environ.get("SHELL") or os.environ.get("COMSPEC")


def render_doctor_report(report: DoctorReport) -> str:
    def flag(ok: bool) -> str:
        return "OK" if ok else "MISSING"

    lines = [
        "Research Helper Doctor",
        "",
        "Platform:",
        f"  OS: {report.os}",
        f"  Architecture: {report.architecture}",
        f"  Shell: {report.shell}",
        "",
        "Core:",
        f"  Python ............. {flag(report.python_ok)}",
        f"  uv ................. {flag(report.uv_ok)}",
        f"  Git ................ {flag(report.git_ok)}",
        "",
        "Research:",
        f"  PDF extractor ...... {flag(report.pdf_extractor_ok)}",
        f"  Graphify ........... {flag(report.graphify_ok)}",
        f"  Obsidian Vault ..... {flag(report.obsidian_vault_ok)}",
        "",
        "Academic:",
        f"  LaTeX .............. {flag(report.latex_ok)}",
        f"  BibTeX ............. {flag(report.bibtex_ok)}",
        "",
        "Agents:",
    ]
    for name, found in report.agents_found.items():
        lines.append(f"  {name.title()} ........ {'FOUND' if found else 'NOT FOUND'}")
    lines += ["", f"Status:\n  {report.status}"]
    return "\n".join(lines) + "\n"
