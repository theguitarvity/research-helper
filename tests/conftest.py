import pytest


@pytest.fixture
def lab_dir(tmp_path):
    return tmp_path / "lab"
