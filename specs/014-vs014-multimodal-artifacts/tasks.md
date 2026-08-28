# Tasks: Multimodal Artifacts

- [ ] T001 `research_helper/multimodal.py`: `FigureMetadata` model (FR-002)
- [ ] T002 `extract_images(paper_dir, reader=None) -> list[FigureMetadata]` (FR-001, FR-002)
- [ ] T003 `record_figure_analysis(paper_dir, figure_id, *, caption=None,
      analysis=None, analysis_model=None) -> FigureMetadata` (FR-003)
- [ ] T004 `create_delegation_task(paths, *, capability, reason) -> Path` (FR-004)
- [ ] T005 `research_helper/cli.py`: no CLI command required this slice
      (invoked programmatically by the agent during multimodal analysis)
- [ ] T010 `tests/test_multimodal.py::test_extract_images_from_fake_reader` (SC-001)
- [ ] T011 `tests/test_multimodal.py::test_record_figure_analysis_updates_only_given_fields` (SC-002)
- [ ] T012 `tests/test_multimodal.py::test_create_delegation_task_writes_file` (SC-003)
