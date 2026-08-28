# Tasks: Open Access Acquisition

- [ ] T001 `research_helper/references.py`: add `pdf_url`, `open_access`,
      `acquisition_state`, `local_path` to `ResolvedReference`; carry
      `pdf_url`/`open_access` through `_to_resolved` (FR-001)
- [ ] T002 `research_helper/acquisition.py`: `Downloader` Protocol (FR-005)
- [ ] T003 `_cache_path(paths, url) -> Path` (FR-006)
- [ ] T004 `acquire_reference(paths, ref, downloader) -> ResolvedReference`
      (FR-002, FR-003, FR-004)
- [ ] T005 `acquire_references(paths, paper_dir, refs, downloader) ->
      list[ResolvedReference]`, rewrites `references.resolved.json`
- [ ] T006 `research_helper/cli.py`: `references download <paper-id>` command
- [ ] T010 `tests/test_acquisition.py::test_oa_reference_downloaded` (SC-001)
- [ ] T011 `tests/test_acquisition.py::test_confirmed_non_oa_is_paywalled` (SC-002)
- [ ] T012 `tests/test_acquisition.py::test_unconfirmed_is_metadata_only`
- [ ] T013 `tests/test_acquisition.py::test_cache_avoids_second_fetch_call` (SC-003)
