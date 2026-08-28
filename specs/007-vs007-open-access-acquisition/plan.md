# Implementation Plan: Open Access Acquisition

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.acquisition`: `Downloader` Protocol, content-hash cache
under `LabPaths.cache_dir`, `acquire_references`. Extend
`ResolvedReference` (in `references.py`) with `pdf_url`, `open_access`,
`acquisition_state`, `local_path`.

## Constitution Check

Principle V (legal/ethical acquisition, non-negotiable): only
`open_access` URLs are ever fetched; no bypass path exists. PASS.

## Project Structure

```text
research_helper/acquisition.py
tests/test_acquisition.py
```
