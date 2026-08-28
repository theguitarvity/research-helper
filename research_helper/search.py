"""Scientific search: normalized schema, dedup, reproducible manifest
(VS003, `fundactional.md` §7, §38).

Deterministic orchestration only (constitution Principle III) — actual
HTTP calls live behind the `SearchClient` protocol in
`research_helper.search_clients`, so this module is fully unit-testable
offline with fake clients.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import yaml
from pydantic import BaseModel, Field

from research_helper.lab import LabPaths


class SearchResult(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    venue: str | None = None
    abstract: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    open_access: bool = False
    source: str


class SearchQuery(BaseModel):
    query: str
    date_from: int | None = None
    date_to: int | None = None
    languages: list[str] = Field(default_factory=list)
    max_results: int = 100
    sources: list[str] = Field(default_factory=lambda: ["semantic-scholar", "crossref", "openalex"])


class SearchClient(Protocol):
    name: str

    def search(self, query: SearchQuery) -> list[SearchResult]: ...


def normalize_title(title: str) -> str:
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return re.sub(r"\s+", " ", text)


def dedup(results: list[SearchResult]) -> list[SearchResult]:
    """DOI -> normalized title -> authors+year priority (FR-003)."""
    by_doi: dict[str, SearchResult] = {}
    by_title: dict[str, SearchResult] = {}
    by_authors_year: dict[tuple[str, int], SearchResult] = {}
    ordered: list[SearchResult] = []

    for r in results:
        doi_key = r.doi.strip().lower() if r.doi else None
        title_key = normalize_title(r.title) if r.title else None
        ay_key = (
            (",".join(sorted(a.lower() for a in r.authors)), r.year)
            if r.authors and r.year
            else None
        )

        if doi_key and doi_key in by_doi:
            continue
        if not doi_key and title_key and title_key in by_title:
            continue
        if not doi_key and not title_key and ay_key and ay_key in by_authors_year:
            continue

        if doi_key:
            by_doi[doi_key] = r
        if title_key:
            by_title[title_key] = r
        if ay_key:
            by_authors_year[ay_key] = r
        ordered.append(r)

    return ordered


def _slugify(text: str) -> str:
    slug = normalize_title(text).replace(" ", "-")
    return slug[:60].strip("-") or "search"


def run_search(
    paths: LabPaths,
    query: SearchQuery,
    clients: list[SearchClient],
) -> list[SearchResult]:
    """Run `query` against every client, dedup, persist a manifest."""
    raw_by_source: dict[str, list[dict]] = {}
    failures: dict[str, str] = {}
    all_results: list[SearchResult] = []

    for client in clients:
        try:
            client_results = client.search(query)
        except Exception as exc:  # noqa: BLE001 - one source failing must not abort the search
            failures[client.name] = str(exc)
            continue
        raw_by_source[client.name] = [r.model_dump(mode="json") for r in client_results]
        all_results.extend(client_results)

    normalized = dedup(all_results)

    now = datetime.now(UTC)
    executed_at = now.isoformat()
    manifest_dir = paths.searches_dir / f"{now.date().isoformat()}-{_slugify(query.query)}"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    (manifest_dir / "query.yaml").write_text(
        yaml.safe_dump({**query.model_dump(mode="json"), "executed_at": executed_at}, sort_keys=False),
        encoding="utf-8",
    )
    _write_json(manifest_dir / "raw-results.json", raw_by_source)
    _write_json(manifest_dir / "normalized.json", [r.model_dump(mode="json") for r in normalized])
    _write_json(manifest_dir / "selected.json", [r.model_dump(mode="json") for r in normalized])

    readme_lines = [
        f"# Search: {query.query}",
        "",
        f"Executed at: {executed_at}",
        f"Sources queried: {', '.join(c.name for c in clients)}",
        f"Results (post-dedup): {len(normalized)}",
    ]
    if failures:
        readme_lines += ["", "## Failed sources", ""]
        readme_lines += [f"- {name}: {msg}" for name, msg in failures.items()]
    (manifest_dir / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    return normalized


def _write_json(path: Path, data) -> None:
    import json

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
