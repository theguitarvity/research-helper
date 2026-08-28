"""Three-level citation validation (VS009, `fundactional.md` §9, §35-36).

Level 1 (Existence) and Level 2 (Bibliographic Consistency) are derived
deterministically from VS006's `ResolvedReference`. Level 3 (Claim
Support) is agent-supplied — reading a claim against a cited paper is
reasoning work (constitution Principle III), so this module validates
and persists that judgment, it does not compute it.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from research_helper.references import ResolvedReference

ExistenceState = Literal["VERIFIED", "RESOLVED", "UNVERIFIED", "SUSPECTED_INVALID"]
ClaimSupport = Literal[
    "SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "CONTRADICTED", "UNCLEAR"
]


class CitationValidation(BaseModel):
    raw_text: str
    doi: str | None = None
    existence_state: ExistenceState
    consistency_flags: list[str] = Field(default_factory=list)
    claim_support: ClaimSupport | None = None
    evidence: str | None = None
    justification: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


def validate_citation(
    resolved_ref: ResolvedReference,
    *,
    claim_support: ClaimSupport | None = None,
    evidence: str | None = None,
    justification: str | None = None,
    confidence: float | None = None,
) -> CitationValidation:
    """FR-002, FR-003: Level 1/2 derived; Level 3 taken as given."""
    if resolved_ref.state in ("VERIFIED", "RESOLVED"):
        existence_state: ExistenceState = resolved_ref.state  # type: ignore[assignment]
    else:
        existence_state = "UNVERIFIED"

    return CitationValidation(
        raw_text=resolved_ref.raw_text,
        doi=resolved_ref.doi,
        existence_state=existence_state,
        consistency_flags=list(resolved_ref.consistency_flags),
        claim_support=claim_support,
        evidence=evidence,
        justification=justification,
        confidence=confidence,
    )


def mark_suspected_invalid(validation: CitationValidation) -> CitationValidation:
    """FR-004: UNVERIFIED must precede SUSPECTED_INVALID — never skip it."""
    if validation.existence_state != "UNVERIFIED":
        raise ValueError(
            "Cannot mark SUSPECTED_INVALID from "
            f"'{validation.existence_state}' — must pass through UNVERIFIED first."
        )
    return validation.model_copy(update={"existence_state": "SUSPECTED_INVALID"})


def validate_citations(
    paper_dir: Path,
    resolved_refs: list[ResolvedReference],
    claims: dict[str, dict] | None = None,
) -> list[CitationValidation]:
    """FR-006: validate every reference, write citations.json.

    `claims` optionally maps a reference's `raw_text` to agent-supplied
    `claim_support`/`evidence`/`justification`/`confidence`.
    """
    claims = claims or {}
    validations = [
        validate_citation(ref, **claims.get(ref.raw_text, {})) for ref in resolved_refs
    ]
    path = Path(paper_dir) / "citations.json"
    path.write_text(
        json.dumps([v.model_dump() for v in validations], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return validations
