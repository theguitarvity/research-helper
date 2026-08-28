# Implementation Plan: Experiment Scaffolder

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.experiments`: `EXPERIMENT_SUBDIRS`, `init_experiment`,
sequential `EXP-NNN` id assignment. CLI: `experiment init`.

## Constitution Check

Principle III (script-first, deterministic scaffolding): PASS.

## Project Structure

```text
research_helper/experiments.py
tests/test_experiments.py
```
