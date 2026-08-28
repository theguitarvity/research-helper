"""Multimodal artifacts: figure extraction + capability delegation
(VS014, `fundactional.md` §18, §39).

Extraction is mechanical (deterministic, pypdf); captions/analysis are
agent-supplied — reasoning work, same script/agent boundary as VS008/
VS009. `reader` is injectable so tests never need real embedded-image
bytes (mirrors the `SearchClient`/`Downloader` pattern).
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from pydantic import BaseModel

from research_helper.lab import LabPaths
from research_helper.synthesis import NOT_DEFINED


class PdfImage(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def data(self) -> bytes: ...


class PdfPage(Protocol):
    @property
    def images(self) -> Sequence[PdfImage]: ...


class PdfReaderLike(Protocol):
    @property
    def pages(self) -> Sequence[PdfPage]: ...


class FigureMetadata(BaseModel):
    paper: str
    page: int
    figure: str
    caption: str | None = None
    extraction_method: str = "pypdf"
    analysis_model: str | None = None


def _figures_dir(paper_dir: Path) -> Path:
    d = Path(paper_dir) / "figures"
    d.mkdir(parents=True, exist_ok=True)
    return d


def extract_images(paper_dir: Path, reader: PdfReaderLike | None = None) -> list[FigureMetadata]:
    """FR-001, FR-002: mechanical extraction only — no caption/analysis."""
    paper_dir = Path(paper_dir)
    active_reader: PdfReaderLike
    if reader is None:
        from pypdf import PdfReader

        active_reader = PdfReader(str(paper_dir / "paper.pdf"))
    else:
        active_reader = reader

    figures_dir = _figures_dir(paper_dir)
    results: list[FigureMetadata] = []
    counter = 0

    for page_num, page in enumerate(active_reader.pages, start=1):
        for image in page.images:
            counter += 1
            figure_id = f"figure-{counter:03d}"
            ext = Path(image.name).suffix.lstrip(".") or "png"

            (figures_dir / f"{figure_id}.{ext}").write_bytes(image.data)

            metadata = FigureMetadata(
                paper=paper_dir.name, page=page_num, figure=figure_id
            )
            (figures_dir / f"{figure_id}.json").write_text(
                metadata.model_dump_json(indent=2), encoding="utf-8"
            )
            (figures_dir / f"{figure_id}.analysis.md").write_text(
                NOT_DEFINED + "\n", encoding="utf-8"
            )
            results.append(metadata)

    return results


def record_figure_analysis(
    paper_dir: Path,
    figure_id: str,
    *,
    caption: str | None = None,
    analysis: str | None = None,
    analysis_model: str | None = None,
) -> FigureMetadata:
    """FR-003: update only the fields given, never fabricate the rest."""
    figures_dir = _figures_dir(paper_dir)
    metadata_path = figures_dir / f"{figure_id}.json"
    metadata = FigureMetadata.model_validate_json(metadata_path.read_text(encoding="utf-8"))

    if caption is not None:
        metadata.caption = caption
    if analysis_model is not None:
        metadata.analysis_model = analysis_model
    metadata_path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")

    if analysis is not None:
        (figures_dir / f"{figure_id}.analysis.md").write_text(analysis + "\n", encoding="utf-8")

    return metadata


def create_delegation_task(paths: LabPaths, *, capability: str, reason: str) -> Path:
    """FR-004: explicit CAPABILITY_UNAVAILABLE record — never a silent skip."""
    delegations_dir = paths.state_dir / "delegations"
    delegations_dir.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "id": str(uuid4()),
        "capability": capability,
        "state": "CAPABILITY_UNAVAILABLE",
        "reason": reason,
        "created_at": datetime.now(UTC).isoformat(),
    }
    dest = delegations_dir / f"{record['id']}.json"
    dest.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest
