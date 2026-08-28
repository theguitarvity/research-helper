# Implementation Plan: Reference Resolution

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

Extend `research_helper.references` with `ResolvedReference`,
`resolve_reference`/`resolve_references`, reusing `SearchClient` +
`SearchQuery` from `research_helper.search` (no new client abstraction).
BibTeX rendering via a small internal helper (no new dependency — BibTeX
entries are simple enough to template directly).

## Technical Context

**Dependencies**: none new — reuses `research_helper.search`'s
`SearchClient`, and stdlib `difflib` for title similarity.

## Constitution Check

Principle IV (evidence-first): resolution always queries external
sources; consistency mismatches are recorded, never silently resolved in
the citation's favor. PASS.

## Project Structure

```text
research_helper/references.py   # + ResolvedReference, resolve_*, bibtex
tests/test_reference_resolution.py
```
