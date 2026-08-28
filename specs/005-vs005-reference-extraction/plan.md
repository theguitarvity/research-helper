# Implementation Plan: Reference Extraction

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.references`: text extraction via `pypdf`, heading-based
section detection, regex-based splitting/DOI capture, `RawReference`
model, `extract_references`. CLI: `research-helper references extract`.

## Technical Context

**Primary Dependencies**: `pypdf` (new — added to `pyproject.toml`; the
ADR deferred in `tech-stack.md` is resolved here: pypdf over
`pdfminer.six` because it's pure-Python, has no compiled dependency risk,
and is sufficient for text extraction at this MVP stage).

**Testing**: hand-built minimal single-page PDFs (`tests/pdf_fixtures.py`,
no new dependency) with known reference text, so extraction is verified
against real `pypdf` parsing rather than mocked text.

## Constitution Check

Principle III (script-first, no LLM for a deterministic step): PASS.
Development Workflow (fixtures for deterministic tests, §49): PASS via
hand-built PDF fixtures.

## Project Structure

```text
research_helper/references.py
tests/pdf_fixtures.py
tests/test_references.py
```
