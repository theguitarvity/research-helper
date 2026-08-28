# Implementation Plan: Research Lineage

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.lineage`: `LineageNode`/`LineageEdge`/`LineageGraph`
models (shape mirrors `research_helper.graph`'s pattern but for the §37
domain), `add_node`, `add_edge`, `trace_back`, `save_lineage`/
`load_lineage`.

## Constitution Check

Principle IV (§10 SOURCE FACT / AGENT INTERPRETATION / RESEARCHER
DECISION, never mixed): enforced by making `classification` a required,
single-valued `Literal` field. PASS.

## Project Structure

```text
research_helper/lineage.py
tests/test_lineage.py
```
