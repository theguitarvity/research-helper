# Tasks: Citation Validation

- [ ] T001 `research_helper/citations.py`: `CitationValidation` model (FR-001, FR-005)
- [ ] T002 `validate_citation(resolved_ref, *, claim_support=None,
      evidence=None, justification=None, confidence=None) ->
      CitationValidation` (FR-002, FR-003)
- [ ] T003 `mark_suspected_invalid(validation) -> CitationValidation` (FR-004)
- [ ] T004 `validate_citations(paper_dir, resolved_refs, claims=None) ->
      list[CitationValidation]`, writes `citations.json` (FR-006)
- [ ] T005 `research_helper/cli.py`: `citations validate <paper-id>` command
- [ ] T010 `tests/test_citations.py::test_existence_state_mapping` (SC-001)
- [ ] T011 `tests/test_citations.py::test_mark_suspected_invalid_requires_unverified` (SC-002)
- [ ] T012 `tests/test_citations.py::test_confidence_out_of_range_rejected` (SC-003)
- [ ] T013 `tests/test_citations.py::test_consistency_flags_carried_verbatim`
