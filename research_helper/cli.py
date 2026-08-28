"""Thin Typer CLI over research_helper's core modules.

Constitution Principle III (script-first): command bodies only parse
args, call a core function, and render output — no business logic here.
"""
from __future__ import annotations

import json
from pathlib import Path

import typer

from research_helper import lab
from research_helper.acquisition import HttpxDownloader, acquire_references
from research_helper.citations import validate_citations
from research_helper.experiments import init_experiment
from research_helper.graph import build_graph
from research_helper.paper_project import init_paper_project
from research_helper.papers import import_paper
from research_helper.references import (
    RawReference,
    ResolvedReference,
    extract_references,
    resolve_references,
)
from research_helper.search import SearchClient, SearchQuery, run_search
from research_helper.search_clients import CrossrefClient, OpenAlexClient, SemanticScholarClient
from research_helper.synthesis import PaperSynthesis, write_individual_synthesis
from research_helper.vault import sync_vault, write_current_context

app = typer.Typer(help="Research Helper — agentic research engineering harness.")
references_app = typer.Typer(help="Reference extraction/resolution/download.")
app.add_typer(references_app, name="references")

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


@app.command(name="import")
def import_command(
    file: str = typer.Argument(..., help="Path to the PDF to import."),
    doi: str | None = typer.Option(None, "--doi"),
    source: str = typer.Option("researcher-supplied", "--source"),
    license: str | None = typer.Option(None, "--license"),
    open_access: bool = typer.Option(False, "--open-access"),
) -> None:
    """Import a PDF into the library under a stable, provenance-tracked id."""
    paths = lab.LabPaths.resolve()
    paper_dir = import_paper(
        paths, Path(file), doi=doi, source=source, license=license, open_access=open_access
    )
    typer.echo(f"Imported into {paper_dir}")


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


@references_app.command("extract")
def references_extract(
    paper: str = typer.Argument(..., help="Paper identifier under library/papers/."),
) -> None:
    """Extract references from an imported paper's PDF."""
    paths = lab.LabPaths.resolve()
    paper_dir = paths.library_papers_dir / paper
    refs = extract_references(paper_dir)
    typer.echo(f"{len(refs)} references discovered")


@references_app.command("resolve")
def references_resolve(
    paper: str = typer.Argument(..., help="Paper identifier under library/papers/."),
) -> None:
    """Resolve a paper's normalized references against external sources."""
    paths = lab.LabPaths.resolve()
    paper_dir = paths.library_papers_dir / paper
    normalized = json.loads((paper_dir / "references.normalized.json").read_text())
    refs = [RawReference(**r) for r in normalized]
    clients = list(_ALL_CLIENTS.values())
    resolved = resolve_references(paper_dir, refs, clients)
    counts: dict[str, int] = {}
    for r in resolved:
        counts[r.state] = counts.get(r.state, 0) + 1
    typer.echo(", ".join(f"{n} {state.lower()}" for state, n in counts.items()) or "0 resolved")


@references_app.command("download")
def references_download(
    paper: str = typer.Argument(..., help="Paper identifier under library/papers/."),
) -> None:
    """Download open-access PDFs for a paper's resolved references."""
    paths = lab.LabPaths.resolve()
    paper_dir = paths.library_papers_dir / paper
    resolved = json.loads((paper_dir / "references.resolved.json").read_text())
    refs = [ResolvedReference(**r) for r in resolved]
    updated = acquire_references(paths, paper_dir, refs, HttpxDownloader())
    counts: dict[str, int] = {}
    for r in updated:
        counts[r.acquisition_state or "UNKNOWN"] = counts.get(r.acquisition_state or "UNKNOWN", 0) + 1
    typer.echo(", ".join(f"{n} {state.lower()}" for state, n in counts.items()) or "nothing to download")


@app.command()
def summarize(
    paper: str = typer.Argument(..., help="Paper identifier under library/papers/."),
    from_json: str = typer.Option(
        ..., "--from-json", help="JSON file with agent-computed PaperSynthesis section content."
    ),
) -> None:
    """Persist a structured synthesis for PAPER from agent-computed sections."""
    paths = lab.LabPaths.resolve()
    sections = json.loads(Path(from_json).read_text())
    dest = write_individual_synthesis(paths, paper, PaperSynthesis(**sections))
    typer.echo(f"Synthesis written to {dest}")


citations_app = typer.Typer(help="Citation validation.")
app.add_typer(citations_app, name="citations")


@citations_app.command("validate")
def citations_validate_command(
    paper: str = typer.Argument(..., help="Paper identifier under library/papers/."),
    claims_json: str | None = typer.Option(
        None, "--claims-json", help="Optional agent-computed Level-3 claim support data."
    ),
) -> None:
    """Validate a paper's resolved references (existence + consistency + claim support)."""
    paths = lab.LabPaths.resolve()
    paper_dir = paths.library_papers_dir / paper
    resolved = json.loads((paper_dir / "references.resolved.json").read_text())
    refs = [ResolvedReference(**r) for r in resolved]
    claims = json.loads(Path(claims_json).read_text()) if claims_json else None
    validations = validate_citations(paper_dir, refs, claims)
    counts: dict[str, int] = {}
    for v in validations:
        counts[v.existence_state] = counts.get(v.existence_state, 0) + 1
    typer.echo(", ".join(f"{n} {state.lower()}" for state, n in counts.items()) or "0 validated")


graph_app = typer.Typer(help="Citation graph.")
app.add_typer(graph_app, name="graph")


@graph_app.command("build")
def graph_build() -> None:
    """Rebuild the citation graph from the library."""
    paths = lab.LabPaths.resolve()
    graph = build_graph(paths)
    typer.echo(f"{len(graph.nodes)} nodes, {len(graph.edges)} edges")


vault_app = typer.Typer(help="Obsidian vault + research memory.")
app.add_typer(vault_app, name="vault")


@vault_app.command("sync")
def vault_sync() -> None:
    """Sync the Obsidian vault and refresh the current-context checkpoint."""
    paths = lab.LabPaths.resolve()
    written = sync_vault(paths)
    write_current_context(paths)
    typer.echo(f"{len(written)} paper note(s) synced; current-context.md refreshed")


experiment_app = typer.Typer(help="Experiment scaffolding.")
app.add_typer(experiment_app, name="experiment")


@experiment_app.command("init")
def experiment_init(
    name: str = typer.Argument(..., help="Experiment name."),
    title: str | None = typer.Option(None, "--title"),
    research_question: str | None = typer.Option(None, "--research-question"),
    hypothesis: str | None = typer.Option(None, "--hypothesis"),
    dataset: str | None = typer.Option(None, "--dataset"),
    reproduction_command: str | None = typer.Option(None, "--reproduction-command"),
) -> None:
    """Scaffold a new experiment under experiments/<name>/."""
    paths = lab.LabPaths.resolve()
    exp_dir = init_experiment(
        paths,
        name,
        title=title,
        research_question=research_question,
        hypothesis=hypothesis,
        dataset=dataset,
        reproduction_command=reproduction_command,
    )
    typer.echo(f"Experiment scaffolded at {exp_dir}")


paper_app = typer.Typer(help="LaTeX paper project scaffolding.")
app.add_typer(paper_app, name="paper")


@paper_app.command("init")
def paper_init(
    venue: str = typer.Option(..., "--venue", help="Registered venue name (or 'generic')."),
    name: str = typer.Option(..., "--name", help="Paper project name."),
) -> None:
    """Scaffold a LaTeX paper project against a registered venue template."""
    paths = lab.LabPaths.resolve()
    project_dir = init_paper_project(paths, venue=venue, name=name)
    typer.echo(f"Paper project scaffolded at {project_dir}")


if __name__ == "__main__":
    app()
