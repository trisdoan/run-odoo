import pytest
from pathlib import Path


@pytest.fixture
def data_dir() -> Path:
    cwd = Path(__file__)
    return cwd.parent / "data"
