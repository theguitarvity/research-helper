"""Reference extraction (VS005, `fundactional.md` §8) and, going forward,
resolution (VS006). Deterministic pipeline, no LLM call (constitution
Principle III): text extraction -> section detection -> splitting -> DOI
capture.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel
from pypdf import PdfReader

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[^\s\)\]\"'>,;]+")
SECTION_HEADING_PATTERN = re.compile(
    r"^\s*(references|bibliography)\s*$", re.IGNORECASE | re.MULTILINE
)
BRACKET_REF_PATTERN = re.compile(r"(?=\[\d+\])")
NUMBERED_REF_PATTERN = re.compile(r"(?=^\d+\.\s)", re.MULTILINE)


class RawReference(BaseModel):
    raw_text: str
    doi: str | None = None
    state: str = "DISCOVERED"


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def detect_references_section(text: str) -> str:
    match = SECTION_HEADING_PATTERN.search(text)
    if not match:
        return ""
    return text[match.end() :]


def extract_doi(text: str) -> str | None:
    match = DOI_PATTERN.search(text)
    if not match:
        return None
    return match.group(0).rstrip(").,;")


def split_references(section: str) -> list[str]:
    section = section.strip()
    if not section:
        return []

    chunks = [c.strip() for c in BRACKET_REF_PATTERN.split(section) if c.strip()]
    if len(chunks) > 1:
        return chunks

    chunks = [c.strip() for c in NUMBERED_REF_PATTERN.split(section) if c.strip()]
    if len(chunks) > 1:
        return chunks

    return [c.strip() for c in re.split(r"\n\s*\n", section) if c.strip()]


def extract_references(paper_dir: Path) -> list[RawReference]:
    """FR-002..FR-006: extract, write raw+normalized, return normalized."""
    paper_dir = Path(paper_dir)
    text = extract_text(paper_dir / "paper.pdf")
    section = detect_references_section(text)
    raw_strings = split_references(section)

    raw_refs = [
        RawReference(raw_text=s, doi=extract_doi(s)) for s in raw_strings if s.strip()
    ]

    seen: set[str] = set()
    normalized_refs: list[RawReference] = []
    for ref in raw_refs:
        normalized_text = re.sub(r"\s+", " ", ref.raw_text).strip()
        if normalized_text in seen:
            continue
        seen.add(normalized_text)
        normalized_refs.append(
            RawReference(raw_text=normalized_text, doi=ref.doi, state=ref.state)
        )

    _write_json(paper_dir / "references.raw.json", [r.model_dump() for r in raw_refs])
    _write_json(
        paper_dir / "references.normalized.json", [r.model_dump() for r in normalized_refs]
    )

    return normalized_refs


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
