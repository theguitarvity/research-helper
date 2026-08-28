"""Open Access acquisition + shared cache (VS007, `fundactional.md` §27-28).

Constitution Principle V (non-negotiable): only `open_access` URLs are
ever fetched here — there is no paywall-bypass code path, by
construction, not by convention.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

import httpx

from research_helper.lab import LabPaths
from research_helper.references import ResolvedReference


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class Downloader(Protocol):
    def fetch(self, url: str) -> bytes: ...


class HttpxDownloader:
    """Real `Downloader` used by the CLI; tests inject a fake instead."""

    def fetch(self, url: str) -> bytes:
        response = httpx.get(url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        return response.content


def _cache_path(paths: LabPaths, url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return paths.cache_dir / "downloads" / f"{digest}.pdf"


def _fetch_cached(paths: LabPaths, url: str, downloader: Downloader) -> bytes:
    cache_path = _cache_path(paths, url)
    if cache_path.is_file():
        return cache_path.read_bytes()
    content = downloader.fetch(url)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(content)
    return content


def acquire_reference(
    paths: LabPaths, paper_dir: Path, ref: ResolvedReference, downloader: Downloader
) -> ResolvedReference:
    """FR-002..FR-004: only download a confirmed, open-access reference."""
    if ref.state not in ("VERIFIED", "RESOLVED"):
        ref.acquisition_state = "METADATA_ONLY"
        return ref

    if not (ref.open_access and ref.pdf_url):
        ref.acquisition_state = "PAYWALLED"
        return ref

    content = _fetch_cached(paths, ref.pdf_url, downloader)
    dest_dir = paper_dir / "references" / "papers"
    dest_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(ref.pdf_url.encode("utf-8")).hexdigest()[:16]
    dest = dest_dir / f"{digest}.pdf"
    dest.write_bytes(content)
    ref.acquisition_state = "DOWNLOADED"
    ref.local_path = str(dest.relative_to(paper_dir))
    return ref


def acquire_references(
    paths: LabPaths,
    paper_dir: Path,
    refs: list[ResolvedReference],
    downloader: Downloader,
) -> list[ResolvedReference]:
    """FR-005..FR-006: acquire every reference, rewrite resolved JSON."""
    updated = [acquire_reference(paths, paper_dir, ref, downloader) for ref in refs]
    _write_json(paper_dir / "references.resolved.json", [r.model_dump() for r in updated])
    return updated
