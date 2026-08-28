# Implementation Plan: Cross-Agent Handoff

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.handoff`: `HandoffRecord` model, `render_handoff_md`,
`create_handoff` (reuses `research_helper.tasks.load_active_task`),
`resume`.

## Constitution Check

Principle II (persistent artifacts over chat history) is this slice's
entire purpose. PASS.

## Project Structure

```text
research_helper/handoff.py
tests/test_handoff.py
```
