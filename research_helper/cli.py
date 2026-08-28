"""Thin Typer CLI over research_helper's core modules.

Constitution Principle III (script-first): command bodies only parse
args, call a core function, and render output — no business logic here.
"""
from __future__ import annotations

from pathlib import Path

import typer

from research_helper import lab

app = typer.Typer(help="Research Helper — agentic research engineering harness.")


@app.callback()
def main() -> None:
    """Research Helper — agentic research engineering harness."""


@app.command()
def init(
    path: str | None = typer.Argument(
        None, help="Directory to initialize as a Research Lab (default: cwd)."
    ),
) -> None:
    """Turn PATH (default: current directory) into a Research Lab."""
    target = Path(path) if path else Path.cwd()
    root = lab.scaffold(target)
    typer.echo(f"Research Lab ready at {root}")


if __name__ == "__main__":
    app()
