# Implementation Plan: Doctor / Validation / Observability

**Spec**: `./spec.md` · **Date**: 2026-08-27

## Summary

`research_helper.doctor`: platform/tool/agent detection + `DoctorReport` +
render. `research_helper.validate`: ten gate-check functions + `validate`
aggregator + `ValidationIssue`. `research_helper.observability`:
`log_event` (fixed keyword set only). `research_helper.config`:
`global_config_dir`. `scripts/bootstrap.{py,sh,ps1}`.

## Technical Context

**Dependencies**: stdlib only (`platform`, `shutil`, `os`, `json`, `re`).

## Constitution Check

Security & Operational Constraints ("logs MUST NEVER record secret
values"): enforced by `log_event`'s fixed signature (no `**kwargs`).
Principle VII (portability): `global_config_dir` covers all four OS
branches. PASS.

## Project Structure

```text
research_helper/doctor.py
research_helper/validate.py
research_helper/observability.py
research_helper/config.py
scripts/bootstrap.py
scripts/bootstrap.sh
scripts/bootstrap.ps1
tests/test_doctor.py
tests/test_validate.py
tests/test_observability.py
tests/test_config.py
```
