"""Structural quality gates (VS017, `fundactional.md` §48).

Each `_check_*` function is one gate; `validate` runs every one of them
and never silently skips a gate, even if it finds nothing to check.

§48 lists ten example defect classes; two of them ("manifest validity"
and "missing hashes") collapse onto the same underlying check here,
since `sha256` missing/invalid IS what makes a manifest invalid in our
`Provenance` schema — `_check_manifests` covers both, tagged
`invalid_manifest`, separately from `missing_provenance` (the file being
absent entirely). *(INFERRED consolidation, recorded per spec.md)*
"""
from __future__ import annotations

import json
import re

import yaml
from pydantic import BaseModel, ValidationError

from research_helper.graph import build_graph
from research_helper.handoff import HandoffRecord
from research_helper.lab import LabPaths
from research_helper.papers import Provenance
from research_helper.references import RawReference, ResolvedReference

WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
LATEX_INPUT_PATTERN = re.compile(r"\\input\{([^}]+)\}")


class ValidationIssue(BaseModel):
    gate: str
    path: str
    message: str


def _paper_dirs(paths: LabPaths) -> list:
    if not paths.library_papers_dir.is_dir():
        return []
    return sorted(p for p in paths.library_papers_dir.iterdir() if p.is_dir())


def _check_reference_schemas(paths: LabPaths) -> list[ValidationIssue]:
    issues = []
    for paper_dir in _paper_dirs(paths):
        for filename, model in (
            ("references.normalized.json", RawReference),
            ("references.resolved.json", ResolvedReference),
        ):
            file_path = paper_dir / filename
            if not file_path.is_file():
                continue
            try:
                for item in json.loads(file_path.read_text(encoding="utf-8")):
                    model.model_validate(item)
            except (ValidationError, json.JSONDecodeError) as exc:
                issues.append(
                    ValidationIssue(gate="schema", path=str(file_path), message=str(exc))
                )
    return issues


def _check_manifests(paths: LabPaths) -> list[ValidationIssue]:
    issues = []
    for paper_dir in _paper_dirs(paths):
        manifest_path = paper_dir / "manifest.json"
        if not manifest_path.is_file():
            issues.append(
                ValidationIssue(
                    gate="missing_provenance", path=str(paper_dir), message="No manifest.json"
                )
            )
            continue
        try:
            Provenance.model_validate_json(manifest_path.read_text(encoding="utf-8"))
        except ValidationError as exc:
            issues.append(
                ValidationIssue(
                    gate="invalid_manifest", path=str(manifest_path), message=str(exc)
                )
            )
    return issues


def _check_duplicate_dois(paths: LabPaths) -> list[ValidationIssue]:
    seen: dict[str, str] = {}
    issues = []
    for paper_dir in _paper_dirs(paths):
        manifest_path = paper_dir / "manifest.json"
        if not manifest_path.is_file():
            continue
        doi = json.loads(manifest_path.read_text(encoding="utf-8")).get("doi")
        if not doi:
            continue
        key = doi.strip().lower()
        if key in seen and seen[key] != paper_dir.name:
            issues.append(
                ValidationIssue(
                    gate="duplicate_doi",
                    path=str(paper_dir),
                    message=f"DOI {doi} also used by {seen[key]}",
                )
            )
        else:
            seen[key] = paper_dir.name
    return issues


def _check_broken_wikilinks(paths: LabPaths) -> list[ValidationIssue]:
    """FR-003: resolve against build_graph's title mapping, not filenames."""
    if not paths.vault_dir.is_dir():
        return []
    graph = build_graph(paths)
    imported_ids = {p.name for p in _paper_dirs(paths)}
    valid_titles = {
        node.properties.get("title") or node.id for node in graph.nodes if node.id in imported_ids
    }

    issues = []
    for md_path in sorted(paths.vault_dir.rglob("*.md")):
        for link in WIKILINK_PATTERN.findall(md_path.read_text(encoding="utf-8")):
            if link not in valid_titles:
                issues.append(
                    ValidationIssue(
                        gate="broken_wikilink", path=str(md_path), message=f"[[{link}]] unresolved"
                    )
                )
    return issues


def _check_bibtex(paths: LabPaths) -> list[ValidationIssue]:
    issues = []
    for paper_dir in _paper_dirs(paths):
        bib_path = paper_dir / "references.bib"
        if not bib_path.is_file():
            continue
        content = bib_path.read_text(encoding="utf-8")
        if content.count("{") != content.count("}"):
            issues.append(
                ValidationIssue(
                    gate="invalid_bibtex", path=str(bib_path), message="Unbalanced braces"
                )
            )
    return issues


def _check_latex(paths: LabPaths) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not paths.paper_projects_dir.is_dir():
        return issues
    for project_dir in sorted(p for p in paths.paper_projects_dir.iterdir() if p.is_dir()):
        main_tex = project_dir / "main.tex"
        if not main_tex.is_file():
            continue
        for ref in LATEX_INPUT_PATTERN.findall(main_tex.read_text(encoding="utf-8")):
            if not (project_dir / f"{ref}.tex").is_file():
                issues.append(
                    ValidationIssue(
                        gate="broken_latex",
                        path=str(main_tex),
                        message=f"\\input{{{ref}}} has no matching file",
                    )
                )
    return issues


def _check_experiment_metadata(paths: LabPaths) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not paths.experiments_dir.is_dir():
        return issues
    for exp_dir in sorted(p for p in paths.experiments_dir.iterdir() if p.is_dir()):
        manifest_path = exp_dir / "manifest.yaml"
        if not manifest_path.is_file():
            issues.append(
                ValidationIssue(
                    gate="missing_experiment_metadata",
                    path=str(exp_dir),
                    message="No manifest.yaml",
                )
            )
            continue
        try:
            yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            issues.append(
                ValidationIssue(
                    gate="missing_experiment_metadata", path=str(manifest_path), message=str(exc)
                )
            )
    return issues


def _check_handoff(paths: LabPaths) -> list[ValidationIssue]:
    handoff_path = paths.state_dir / "handoff.json"
    if not handoff_path.is_file():
        return []
    try:
        HandoffRecord.model_validate_json(handoff_path.read_text(encoding="utf-8"))
    except ValidationError as exc:
        return [ValidationIssue(gate="invalid_handoff", path=str(handoff_path), message=str(exc))]
    return []


def validate(paths: LabPaths) -> list[ValidationIssue]:
    """FR-002: run every §48 gate, never silently skip one."""
    issues: list[ValidationIssue] = []
    issues += _check_reference_schemas(paths)
    issues += _check_manifests(paths)
    issues += _check_duplicate_dois(paths)
    issues += _check_broken_wikilinks(paths)
    issues += _check_bibtex(paths)
    issues += _check_latex(paths)
    issues += _check_experiment_metadata(paths)
    issues += _check_handoff(paths)
    return issues
