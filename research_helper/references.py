"""Reference extraction (VS005, `fundactional.md` §8) and, going forward,
resolution (VS006). Deterministic pipeline, no LLM call (constitution
Principle III): text extraction -> section detection -> splitting -> DOI
capture.
"""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from pydantic import BaseModel, Field
from pypdf import PdfReader

from research_helper.search import SearchClient, SearchQuery, SearchResult, normalize_title

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[^\s\)\]\"'>,;]+")
SECTION_HEADING_PATTERN = re.compile(
    r"^\s*(references|bibliography)\s*$", re.IGNORECASE | re.MULTILINE
)
BRACKET_REF_PATTERN = re.compile(r"(?=\[\d+\])")
NUMBERED_REF_PATTERN = re.compile(r"(?=^\d+\.\s)", re.MULTILINE)
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

# MVP heuristic defaults (INFERRED — not sourced from the context files,
# see spec.md Assumptions). Tunable without changing the public interface.
TITLE_MATCH_THRESHOLD = 0.6
AMBIGUOUS_TIE_MARGIN = 0.05


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


class ResolvedReference(BaseModel):
    raw_text: str
    doi: str | None = None
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    url: str | None = None
    source: str | None = None
    state: str = "UNAVAILABLE"
    consistency_flags: list[str] = Field(default_factory=list)
    pdf_url: str | None = None
    open_access: bool = False
    acquisition_state: str | None = None
    local_path: str | None = None


def extract_citation_year(raw_text: str) -> int | None:
    years = [int(m.group(0)) for m in YEAR_PATTERN.finditer(raw_text)]
    return years[-1] if years else None


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def _candidates_for(ref: RawReference, clients: list[SearchClient]) -> list[SearchResult]:
    query_text = ref.doi or ref.raw_text
    candidates: list[SearchResult] = []
    for client in clients:
        try:
            candidates.extend(client.search(SearchQuery(query=query_text, max_results=3)))
        except Exception:  # noqa: BLE001, S112 - one source failing must not abort resolution
            continue
    return candidates


def resolve_reference(ref: RawReference, clients: list[SearchClient]) -> ResolvedReference:
    """FR-001..FR-005: never trust the citing text alone — always query
    independent external sources before assigning any state above
    DISCOVERED."""
    candidates = _candidates_for(ref, clients)
    cited_year = extract_citation_year(ref.raw_text)

    if not candidates:
        return ResolvedReference(raw_text=ref.raw_text, doi=ref.doi, state="UNAVAILABLE")

    if ref.doi:
        for candidate in candidates:
            if candidate.doi and candidate.doi.strip().lower() == ref.doi.strip().lower():
                return _to_resolved(ref, candidate, "VERIFIED", cited_year)

    scored = sorted(
        ((c, _title_similarity(ref.raw_text, c.title)) for c in candidates),
        key=lambda pair: pair[1],
        reverse=True,
    )
    best, best_score = scored[0]

    if best_score < TITLE_MATCH_THRESHOLD:
        return ResolvedReference(raw_text=ref.raw_text, doi=ref.doi, state="UNAVAILABLE")

    if len(scored) > 1 and (best_score - scored[1][1]) <= AMBIGUOUS_TIE_MARGIN:
        return ResolvedReference(raw_text=ref.raw_text, doi=ref.doi, state="AMBIGUOUS")

    return _to_resolved(ref, best, "RESOLVED", cited_year)


def _to_resolved(
    ref: RawReference, candidate: SearchResult, state: str, cited_year: int | None
) -> ResolvedReference:
    flags = []
    if cited_year and candidate.year and cited_year != candidate.year:
        flags.append(f"year_mismatch: cited={cited_year} resolved={candidate.year}")
    return ResolvedReference(
        raw_text=ref.raw_text,
        doi=candidate.doi or ref.doi,
        title=candidate.title,
        authors=candidate.authors,
        year=candidate.year,
        venue=candidate.venue,
        url=candidate.url,
        source=candidate.source,
        state=state,
        consistency_flags=flags,
        pdf_url=candidate.pdf_url,
        open_access=candidate.open_access,
    )


def resolve_references(
    paper_dir: Path, refs: list[RawReference], clients: list[SearchClient]
) -> list[ResolvedReference]:
    """FR-006, FR-007: resolve every reference, write resolved JSON + BibTeX."""
    paper_dir = Path(paper_dir)
    resolved = [resolve_reference(ref, clients) for ref in refs]
    _write_json(paper_dir / "references.resolved.json", [r.model_dump() for r in resolved])
    (paper_dir / "references.bib").write_text(to_bibtex(resolved), encoding="utf-8")
    return resolved


def _bibtex_key(ref: ResolvedReference, index: int) -> str:
    if ref.doi:
        return re.sub(r"[^A-Za-z0-9]+", "", ref.doi)
    return f"ref{index}"


def to_bibtex(resolved_refs: list[ResolvedReference]) -> str:
    """Only real, resolved fields are emitted — UNAVAILABLE/AMBIGUOUS
    references get a comment-only stub, never a fabricated entry."""
    entries = []
    for i, ref in enumerate(resolved_refs, start=1):
        if ref.state in ("UNAVAILABLE", "AMBIGUOUS"):
            entries.append(f"% {ref.state}: {ref.raw_text}")
            continue
        fields = [f'  title = {{{ref.title or ""}}}']
        if ref.authors:
            fields.append(f'  author = {{{" and ".join(ref.authors)}}}')
        if ref.year:
            fields.append(f"  year = {{{ref.year}}}")
        if ref.venue:
            fields.append(f'  journal = {{{ref.venue}}}')
        if ref.doi:
            fields.append(f'  doi = {{{ref.doi}}}')
        entries.append(
            "@article{" + _bibtex_key(ref, i) + ",\n" + ",\n".join(fields) + "\n}"
        )
    return "\n\n".join(entries) + ("\n" if entries else "")
