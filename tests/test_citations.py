import json

import pytest

from research_helper.citations import (
    CitationValidation,
    mark_suspected_invalid,
    validate_citation,
    validate_citations,
)
from research_helper.references import ResolvedReference


def resolved(**overrides):
    base = {"raw_text": "[1] Some ref.", "state": "UNAVAILABLE"}
    base.update(overrides)
    return ResolvedReference(**base)


@pytest.mark.parametrize(
    "resolution_state,expected",
    [
        ("VERIFIED", "VERIFIED"),
        ("RESOLVED", "RESOLVED"),
        ("AMBIGUOUS", "UNVERIFIED"),
        ("UNAVAILABLE", "UNVERIFIED"),
    ],
)
def test_existence_state_mapping(resolution_state, expected):
    validation = validate_citation(resolved(state=resolution_state))
    assert validation.existence_state == expected


def test_mark_suspected_invalid_requires_unverified():
    verified = validate_citation(resolved(state="VERIFIED"))
    with pytest.raises(ValueError, match="UNVERIFIED"):
        mark_suspected_invalid(verified)

    unverified = validate_citation(resolved(state="UNAVAILABLE"))
    escalated = mark_suspected_invalid(unverified)
    assert escalated.existence_state == "SUSPECTED_INVALID"


def test_confidence_out_of_range_rejected():
    with pytest.raises(ValueError):
        CitationValidation(raw_text="x", existence_state="VERIFIED", confidence=1.5)


def test_consistency_flags_carried_verbatim():
    ref = resolved(state="VERIFIED", consistency_flags=["year_mismatch: cited=2021 resolved=2020"])
    validation = validate_citation(ref)
    assert validation.consistency_flags == ["year_mismatch: cited=2021 resolved=2020"]


def test_validate_citations_writes_file_and_applies_claims(tmp_path):
    refs = [resolved(raw_text="[1] A.", state="VERIFIED"), resolved(raw_text="[2] B.")]
    claims = {"[1] A.": {"claim_support": "SUPPORTED", "confidence": 0.9}}

    validations = validate_citations(tmp_path, refs, claims)

    assert validations[0].claim_support == "SUPPORTED"
    assert validations[1].claim_support is None
    saved = json.loads((tmp_path / "citations.json").read_text())
    assert len(saved) == 2
