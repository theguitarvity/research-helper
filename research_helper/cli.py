"""Thin Typer CLI over research_helper's core modules.

Constitution Principle III (script-first): command bodies only parse
args, call a core function, and render output — no business logic here.
"""
from __future__ import annotations

import json
from pathlib import Path

import typer

from research_helper import lab
from research_helper.search import SearchClient, SearchQuery, run_search
from research_helper.search_clients import CrossrefClient, OpenAlexClient, SemanticScholarClient

app = typer.Typer(help="Research Helper — agentic research engineering harness.")

_ALL_CLIENTS: dict[str, SearchClient] = {
    "semantic-scholar": SemanticScholarClient(),
    "crossref": CrossrefClient(),
    "openalex": OpenAlexClient(),
}


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


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query string."),
    from_year: int | None = typer.Option(None, "--from", help="Earliest publication year."),
    to_year: int | None = typer.Option(None, "--to", help="Latest publication year."),
    sources: str = typer.Option(
        "semantic-scholar,crossref,openalex", "--sources", help="Comma-separated source list."
    ),
    max_results: int = typer.Option(100, "--max-results"),
    format: str = typer.Option("text", "--format", help="text or json"),
) -> None:
    """Search scientific literature across the configured sources."""
    paths = lab.LabPaths.resolve()
    source_names = [s.strip() for s in sources.split(",") if s.strip()]
    clients = [_ALL_CLIENTS[name] for name in source_names if name in _ALL_CLIENTS]
    search_query = SearchQuery(
        query=query,
        date_from=from_year,
        date_to=to_year,
        max_results=max_results,
        sources=source_names,
    )
    results = run_search(paths, search_query, clients)
    if format == "json":
        typer.echo(json.dumps([r.model_dump(mode="json") for r in results], indent=2))
    else:
        typer.echo(f"{len(results)} result(s) found.")
        for r in results:
            typer.echo(f"- {r.title} ({r.year or '?'}) [{r.source}]")


if __name__ == "__main__":
    app()
