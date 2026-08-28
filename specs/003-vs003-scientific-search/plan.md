# Implementation Plan: Scientific Search

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.search`: `SearchResult`/`SearchQuery` models, a
`SearchClient` Protocol, dedup logic, and manifest writer.
`research_helper.search_clients`: concrete `SemanticScholarClient`,
`CrossrefClient`, `OpenAlexClient` over `httpx`. CLI: `research-helper
search`.

## Technical Context

**Language/Version**: Python 3.12+ · **Primary Dependencies**: httpx,
Pydantic · **Testing**: pytest + `respx` (mocks `httpx` transport) for
client parsing; plain fakes implementing `SearchClient` for
orchestration/dedup tests · **Storage**: filesystem manifest under
`literature/searches/`

## Constitution Check

- Principle III (script-first): dedup/normalization/manifest writing are
  pure deterministic code, no LLM. PASS.
- Principle IV (evidence-first): every result carries its `source`
  field; nothing is fabricated — only what a client returns is
  persisted. PASS.
- Development Workflow gate (external APIs mockable): `SearchClient`
  Protocol enforces this. PASS.

## Project Structure

```text
research_helper/search.py           # models, dedup, run_search, manifest
research_helper/search_clients.py   # httpx-backed SearchClient impls
tests/test_search.py                # dedup + manifest, fake clients
tests/test_search_clients.py        # respx-mocked real client parsing
```
