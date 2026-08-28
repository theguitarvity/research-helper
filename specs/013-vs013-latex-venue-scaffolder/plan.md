# Implementation Plan: LaTeX / Venue Scaffolder

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.lab`: add `venues_dir` property. `research_helper.paper_project`:
`load_venue`, `BUILTIN_GENERIC_VENUE`, `init_paper_project`.

## Constitution Check

Principle IV (never fabricate): `load_venue`'s hard failure on an
unregistered non-generic venue is the enforcement point. PASS.

## Project Structure

```text
research_helper/lab.py           # + venues_dir property
research_helper/paper_project.py
tests/test_paper_project.py
```
