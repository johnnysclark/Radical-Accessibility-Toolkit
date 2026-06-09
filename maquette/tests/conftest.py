import pytest

from maquette.engine import Engine
from maquette.project import init_project


@pytest.fixture
def project(tmp_path):
    return init_project(str(tmp_path / "proj"), name="testproj")


@pytest.fixture
def engine(project):
    return Engine(project, backend="record", actor="test")
