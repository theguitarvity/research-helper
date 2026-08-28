"""Paper import + provenance (VS004, `fundactional.md` §25-26)."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from research_helper.lab import LabPaths

HASH_PREFIX_LEN = 16


class Provenance(BaseModel):
    source: str
    original_url: str | None = None
    doi: str | None = None
    retrieved_at: str
    sha256: str
    license: str | None = None
    open_access: bool = False


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def paper_identifier(doi: str | None, sha256: str) -> str:
    if doi:
        return doi.replace("/", "_")
    return f"paper-{sha256[:HASH_PREFIX_LEN]}"


def import_paper(
    paths: LabPaths,
    file_path: Path,
    *,
    doi: str | None = None,
    source: str = "researcher-supplied",
    original_url: str | None = None,
    license: str | None = None,
    open_access: bool = False,
) -> Path:
    """Import `file_path` into `library/papers/<identifier>/` (FR-001..005)."""
    file_path = Path(file_path)
    digest = sha256_of(file_path)
    identifier = paper_identifier(doi, digest)
    paper_dir = paths.library_papers_dir / identifier
    paper_dir.mkdir(parents=True, exist_ok=True)

    dest_pdf = paper_dir / "paper.pdf"
    if not dest_pdf.exists():
        shutil.copy2(file_path, dest_pdf)

    manifest_path = paper_dir / "manifest.json"
    if not manifest_path.exists():
        provenance = Provenance(
            source=source,
            original_url=original_url,
            doi=doi,
            retrieved_at=datetime.now(UTC).isoformat(),
            sha256=digest,
            license=license,
            open_access=open_access,
        )
        manifest_path.write_text(provenance.model_dump_json(indent=2), encoding="utf-8")

    metadata_path = paper_dir / "metadata.json"
    if not metadata_path.exists():
        metadata_path.write_text(
            json.dumps({"doi": doi, "title": None}, indent=2), encoding="utf-8"
        )

    return paper_dir
