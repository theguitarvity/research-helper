# Implementation Plan: Structured Paper Synthesis

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.synthesis`: `PaperSynthesis` model (17 optional
sections), `render_synthesis`, `write_individual_synthesis`,
`write_comparative_synthesis`. CLI: `summarize --from-json`.

## Constitution Check

Principle III (script vs. agent reasoning boundary) is the entire design
driver here — see spec.md's Architecture note. PASS by construction.

## Project Structure

```text
research_helper/synthesis.py
tests/test_synthesis.py
```
