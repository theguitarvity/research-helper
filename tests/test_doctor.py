from research_helper import lab
from research_helper.doctor import render_doctor_report, run_doctor


def test_doctor_detects_python_and_git(lab_dir):
    lab.scaffold(lab_dir)
    paths = lab.LabPaths.resolve(lab_dir)

    report = run_doctor(paths)

    assert report.python_ok is True
    assert report.git_ok is True
    assert report.os in ("Darwin", "Linux", "Windows")


def test_doctor_without_a_lab_still_reports_platform():
    report = run_doctor(None)
    assert report.graphify_ok is False
    assert report.os


def test_render_doctor_report_has_expected_sections(lab_dir):
    lab.scaffold(lab_dir)
    paths = lab.LabPaths.resolve(lab_dir)
    report = run_doctor(paths)

    rendered = render_doctor_report(report)

    for heading in ("Platform:", "Core:", "Research:", "Academic:", "Agents:", "Status:"):
        assert heading in rendered
