from pathlib import Path
import importlib.util
import sys
import types

import pytest

# Load openhands.runtime.utils.files without pulling heavy dependencies
obs_module = types.ModuleType("openhands.events.observation")


class Observation:  # minimal stub
    pass


class ErrorObservation(Observation):
    pass


class FileReadObservation(Observation):
    pass


class FileWriteObservation(Observation):
    pass


obs_module.ErrorObservation = ErrorObservation
obs_module.FileReadObservation = FileReadObservation
obs_module.FileWriteObservation = FileWriteObservation
obs_module.Observation = Observation

events_pkg = types.ModuleType("openhands.events")
events_pkg.__path__ = []

sys.modules.setdefault("openhands.events", events_pkg)
sys.modules.setdefault("openhands.events.observation", obs_module)

spec = importlib.util.spec_from_file_location(
    "files", Path(__file__).resolve().parents[1] / "openhands/runtime/utils/files.py"
)
files = importlib.util.module_from_spec(spec)
spec.loader.exec_module(files)

SANDBOX_PATH_PREFIX = '/workspace'
CONTAINER_PATH = '/workspace'
HOST_PATH = 'workspace'


def test_resolve_path():
    assert (
        files.resolve_path('test.txt', '/workspace', HOST_PATH, CONTAINER_PATH)
        == Path(HOST_PATH) / 'test.txt'
    )
    assert (
        files.resolve_path('subdir/test.txt', '/workspace', HOST_PATH, CONTAINER_PATH)
        == Path(HOST_PATH) / 'subdir' / 'test.txt'
    )
    assert (
        files.resolve_path(
            Path(SANDBOX_PATH_PREFIX) / 'test.txt',
            '/workspace',
            HOST_PATH,
            CONTAINER_PATH,
        )
        == Path(HOST_PATH) / 'test.txt'
    )
    assert (
        files.resolve_path(
            Path(SANDBOX_PATH_PREFIX) / 'subdir' / 'test.txt',
            '/workspace',
            HOST_PATH,
            CONTAINER_PATH,
        )
        == Path(HOST_PATH) / 'subdir' / 'test.txt'
    )
    assert (
        files.resolve_path(
            Path(SANDBOX_PATH_PREFIX) / 'subdir' / '..' / 'test.txt',
            '/workspace',
            HOST_PATH,
            CONTAINER_PATH,
        )
        == Path(HOST_PATH) / 'test.txt'
    )
    with pytest.raises(PermissionError):
        files.resolve_path(
            Path(SANDBOX_PATH_PREFIX) / '..' / 'test.txt',
            '/workspace',
            HOST_PATH,
            CONTAINER_PATH,
        )
    with pytest.raises(PermissionError):
        files.resolve_path(
            Path('..') / 'test.txt', '/workspace', HOST_PATH, CONTAINER_PATH
        )
    with pytest.raises(PermissionError):
        files.resolve_path(
            Path('/') / 'test.txt', '/workspace', HOST_PATH, CONTAINER_PATH
        )
    assert (
        files.resolve_path('test.txt', '/workspace/test', HOST_PATH, CONTAINER_PATH)
        == Path(HOST_PATH) / 'test' / 'test.txt'
    )


def test_insert_lines_replace_whole_file():
    original = ["a\n", "b\n"]
    result = files.insert_lines(["x", "y"], original, 0, -1)
    assert result == ["x\n", "y\n"]


def test_insert_lines_middle_preserves_content():
    original = ["a\n", "b\n", "c\n", "d\n"]
    result = files.insert_lines(["x", "y"], original, 1, 3)
    assert result == ["a\n", "x\n", "y\n", "d\n"]
