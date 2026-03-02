from unittest.mock import MagicMock

import numpy as np
import pytest
from pathlib import Path

from app.models.rag.consts import EMBEDDING_DIMS


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Create a temporary directory with sample RAG text files."""
    (tmp_path / "RAG_File_A.txt").write_text(
        "JUDUL A\n\nSeksi 1\nIni adalah konten pertama.\n\nSeksi 2\nIni konten kedua.",
        encoding="utf-8",
    )
    (tmp_path / "RAG_File_B.txt").write_text(
        "JUDUL B\n\nInformasi penting tentang topik B.",
        encoding="utf-8",
    )
    # Non-RAG file should be ignored
    (tmp_path / "OTHER_file.txt").write_text(
        "This should not be loaded.",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def empty_data_dir(tmp_path):
    """An empty directory with no RAG files."""
    return tmp_path


@pytest.fixture
def real_data_dir():
    """Path to the actual RAG data files in hospital-smart-assistant/data/."""
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    if not data_dir.exists():
        pytest.skip("data/ directory not found")
    return data_dir


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model that returns fake 1024-dim vectors."""
    model = MagicMock()
    model.encode = MagicMock(
        side_effect=lambda chunks: np.random.rand(
            len(chunks) if isinstance(chunks, list) else 1,
            EMBEDDING_DIMS,
        ).astype(np.float32)
    )
    return model
