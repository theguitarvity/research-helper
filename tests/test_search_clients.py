import respx
from httpx import Response

from research_helper.search import SearchQuery
from research_helper.search_clients import CrossrefClient, OpenAlexClient, SemanticScholarClient


@respx.mock
def test_semantic_scholar_client_parses_fixture():
    fixture = {
        "data": [
            {
                "title": "Agentic Software Engineering",
                "authors": [{"name": "Ada Lovelace"}],
                "year": 2025,
                "externalIds": {"DOI": "10.1/abc"},
                "venue": "ICSE",
                "abstract": "An abstract.",
                "openAccessPdf": {"url": "https://example.org/paper.pdf"},
                "url": "https://example.org/paper",
            }
        ]
    }
    respx.get("https://api.semanticscholar.org/graph/v1/paper/search").mock(
        return_value=Response(200, json=fixture)
    )

    results = SemanticScholarClient().search(SearchQuery(query="agentic software engineering"))

    assert len(results) == 1
    r = results[0]
    assert r.title == "Agentic Software Engineering"
    assert r.doi == "10.1/abc"
    assert r.open_access is True
    assert r.source == "semantic-scholar"


@respx.mock
def test_crossref_client_parses_fixture():
    fixture = {
        "message": {
            "items": [
                {
                    "title": ["Harness Engineering"],
                    "author": [{"given": "Ada", "family": "Lovelace"}],
                    "published-print": {"date-parts": [[2024, 6, 1]]},
                    "DOI": "10.2/xyz",
                    "container-title": ["JSS"],
                    "URL": "https://doi.org/10.2/xyz",
                }
            ]
        }
    }
    respx.get("https://api.crossref.org/works").mock(return_value=Response(200, json=fixture))

    results = CrossrefClient().search(SearchQuery(query="harness engineering"))

    assert len(results) == 1
    r = results[0]
    assert r.title == "Harness Engineering"
    assert r.authors == ["Ada Lovelace"]
    assert r.year == 2024
    assert r.doi == "10.2/xyz"
    assert r.source == "crossref"


@respx.mock
def test_openalex_client_parses_fixture():
    fixture = {
        "results": [
            {
                "title": "Semantic Caching for RAG",
                "authorships": [{"author": {"display_name": "Ada Lovelace"}}],
                "publication_year": 2026,
                "doi": "https://doi.org/10.3/def",
                "primary_location": {"source": {"display_name": "arXiv"}},
                "open_access": {"is_oa": True, "oa_url": "https://arxiv.org/pdf/x"},
                "id": "https://openalex.org/W123",
            }
        ]
    }
    respx.get("https://api.openalex.org/works").mock(return_value=Response(200, json=fixture))

    results = OpenAlexClient().search(SearchQuery(query="semantic caching"))

    assert len(results) == 1
    r = results[0]
    assert r.doi == "10.3/def"
    assert r.open_access is True
    assert r.pdf_url == "https://arxiv.org/pdf/x"
    assert r.source == "openalex"
