# Implementation Plan: Citation Validation

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.citations`: `CitationValidation` model (Pydantic
`Literal` for `existence_state`/`claim_support`, `Field(ge=0, le=1)` for
confidence), `validate_citation`, `mark_suspected_invalid`,
`validate_citations`.

## Constitution Check

Principle IV, §35 (UNVERIFIED before SUSPECTED_INVALID, no automatic
accusation): enforced structurally by `mark_suspected_invalid`'s guard.
PASS.

## Project Structure

```text
research_helper/citations.py
tests/test_citations.py
```
