# Implementation Plan: Paper Import

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.papers`: `Provenance` model, `sha256_of`,
`paper_identifier`, `import_paper`. CLI: `research-helper import`.

## Technical Context

Python 3.12+, Pydantic, stdlib `hashlib`/`shutil`. Filesystem only.
Tests use `tmp_path` fixture PDFs (arbitrary bytes — content doesn't need
to be a real PDF for this slice, since no parsing happens yet).

## Constitution Check

Principle IV (evidence-first/provenance): every import records full
provenance, PASS. Principle III (script-first): deterministic hashing/
copying, no LLM, PASS.

## Project Structure

```text
research_helper/papers.py
tests/test_papers.py
```
