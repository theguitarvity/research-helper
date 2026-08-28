# Implementation Plan: Graphify Integration

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.graph`: `GraphNode`/`GraphEdge`/`CitationGraph` models,
`build_graph`, `find_seminal_papers`, `find_isolated_nodes`.

## Constitution Check

Principle III/VI: pure filesystem scan + deterministic assembly, no DB,
no LLM. PASS.

## Project Structure

```text
research_helper/graph.py
tests/test_graph.py
```
