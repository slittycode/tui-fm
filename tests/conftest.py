"""Test fixtures and utilities."""
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_files(temp_dir: Path) -> Path:
    """Create a sample directory structure for testing."""
    # Create files
    (temp_dir / "file1.txt").write_text("Content 1")
    (temp_dir / "file2.py").write_text("print('hello')")
    (temp_dir / "file3.json").write_text('{"key": "value"}')

    # Create subdirectories
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested_file.txt").write_text("Nested content")

    # Create another subdirectory
    subdir2 = temp_dir / "another_dir"
    subdir2.mkdir()
    (subdir2 / "deep_file.md").write_text("# Markdown")

    return temp_dir


@pytest.fixture
def empty_dir(temp_dir: Path) -> Path:
    """Create an empty directory for testing."""
    return temp_dir


@pytest.fixture
def large_file(temp_dir: Path) -> Path:
    """Create a large file (>1MB) for testing."""
    large = temp_dir / "large_file.txt"
    large.write_text("x" * 1_500_000)  # 1.5MB
    return large


@pytest.fixture
def binary_file(temp_dir: Path) -> Path:
    """Create a binary file for testing."""
    binary = temp_dir / "binary.bin"
    binary.write_bytes(b"\x00\x01\x02\x03\x04\x05")
    return binary
