"""httpx-backed SearchClient implementations for public scientific APIs.

Each client only fetches + maps to `SearchResult` (`fundactional.md` §29:
official APIs only). No dedup/manifest logic lives here — that stays in
`research_helper.search` so a client is swappable/mockable in isolation
(constitution "Development Workflow & Quality Gates": external APIs must
be mockable for deterministic tests).

Field mappings follow each API's public documentation but are not
live-verified in this offline environment (see spec.md Assumptions);
`tests/test_search_clients.py` exercises them against fixture payloads
via a mocked `httpx` transport (`respx`).
"""
from __future__ import annotations

import httpx

from research_helper.search import SearchQuery, SearchResult

DEFAULT_TIMEOUT = 15.0


class SemanticScholarClient:
    name = "semantic-scholar"
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "title,authors,year,externalIds,venue,abstract,openAccessPdf,url"

    def search(self, query: SearchQuery) -> list[SearchResult]:
        params: dict[str, str | int] = {
            "query": query.query,
            "limit": query.max_results,
            "fields": self.fields,
        }
        if query.date_from and query.date_to:
            params["year"] = f"{query.date_from}-{query.date_to}"
        response = httpx.get(self.base_url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        results = []
        for item in payload.get("data", []):
            oa_pdf = item.get("openAccessPdf") or {}
            results.append(
                SearchResult(
                    title=item.get("title") or "",
                    authors=[a.get("name", "") for a in item.get("authors", []) if a.get("name")],
                    year=item.get("year"),
                    doi=(item.get("externalIds") or {}).get("DOI"),
                    venue=item.get("venue"),
                    abstract=item.get("abstract"),
                    url=item.get("url"),
                    pdf_url=oa_pdf.get("url"),
                    open_access=bool(oa_pdf.get("url")),
                    source=self.name,
                )
            )
        return results


class CrossrefClient:
    name = "crossref"
    base_url = "https://api.crossref.org/works"

    def search(self, query: SearchQuery) -> list[SearchResult]:
        params: dict[str, str | int] = {"query": query.query, "rows": query.max_results}
        filters = []
        if query.date_from:
            filters.append(f"from-pub-date:{query.date_from}-01-01")
        if query.date_to:
            filters.append(f"until-pub-date:{query.date_to}-12-31")
        if filters:
            params["filter"] = ",".join(filters)
        response = httpx.get(self.base_url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        items = response.json().get("message", {}).get("items", [])
        results = []
        for item in items:
            titles = item.get("title") or [""]
            authors = [
                " ".join(part for part in (a.get("given"), a.get("family")) if part)
                for a in item.get("author", [])
            ]
            year = None
            for date_field in ("published-print", "published", "published-online"):
                parts = (item.get(date_field) or {}).get("date-parts")
                if parts and parts[0]:
                    year = parts[0][0]
                    break
            venues = item.get("container-title") or [None]
            results.append(
                SearchResult(
                    title=titles[0] or "",
                    authors=[a for a in authors if a],
                    year=year,
                    doi=item.get("DOI"),
                    venue=venues[0],
                    abstract=item.get("abstract"),
                    url=item.get("URL"),
                    pdf_url=None,
                    open_access=False,
                    source=self.name,
                )
            )
        return results


class OpenAlexClient:
    name = "openalex"
    base_url = "https://api.openalex.org/works"

    def search(self, query: SearchQuery) -> list[SearchResult]:
        params: dict[str, str | int] = {"search": query.query, "per_page": query.max_results}
        if query.date_from and query.date_to:
            params["filter"] = f"publication_year:{query.date_from}-{query.date_to}"
        response = httpx.get(self.base_url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        results = []
        for item in response.json().get("results", []):
            authorships = item.get("authorships", [])
            open_access = item.get("open_access") or {}
            primary_location = item.get("primary_location") or {}
            source = primary_location.get("source") or {}
            doi = item.get("doi")
            if doi and doi.startswith("https://doi.org/"):
                doi = doi.removeprefix("https://doi.org/")
            results.append(
                SearchResult(
                    title=item.get("title") or "",
                    authors=[
                        (a.get("author") or {}).get("display_name", "")
                        for a in authorships
                        if (a.get("author") or {}).get("display_name")
                    ],
                    year=item.get("publication_year"),
                    doi=doi,
                    venue=source.get("display_name"),
                    abstract=None,
                    url=item.get("id"),
                    pdf_url=open_access.get("oa_url"),
                    open_access=bool(open_access.get("is_oa")),
                    source=self.name,
                )
            )
        return results
