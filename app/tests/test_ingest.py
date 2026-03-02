from pathlib import Path

import pytest

from app.services.ingest import load_documents


class TestLoadDocuments:
    """Tests for load_documents: loads RAG_*.txt files from a directory."""

    def test_loads_only_rag_files(self, tmp_data_dir):
        """Should load files matching RAG_*.txt pattern, ignoring others."""
        docs = load_documents(tmp_data_dir)
        filenames = [name for name, _ in docs]
        assert len(docs) == 2
        assert "RAG_File_A.txt" in filenames
        assert "RAG_File_B.txt" in filenames
        assert "OTHER_file.txt" not in filenames

    def test_returns_filename_and_text_tuples(self, tmp_data_dir):
        """Each item should be a (filename, text_content) tuple."""
        docs = load_documents(tmp_data_dir)
        for filename, text in docs:
            assert isinstance(filename, str)
            assert isinstance(text, str)
            assert len(text) > 0

    def test_returns_sorted_by_filename(self, tmp_data_dir):
        """Results should be sorted alphabetically by filename."""
        docs = load_documents(tmp_data_dir)
        filenames = [name for name, _ in docs]
        assert filenames == sorted(filenames)

    def test_empty_directory_returns_empty_list(self, empty_data_dir):
        """Should return empty list when no RAG files exist."""
        docs = load_documents(empty_data_dir)
        assert docs == []

    def test_nonexistent_directory_raises(self):
        """Should raise FileNotFoundError for non-existent path."""
        with pytest.raises((FileNotFoundError, OSError)):
            load_documents(Path("/nonexistent/path"))

    def test_reads_utf8_content(self, tmp_data_dir):
        """Should correctly read UTF-8 encoded content."""
        docs = load_documents(tmp_data_dir)
        doc_a = next(text for name, text in docs if name == "RAG_File_A.txt")
        assert "konten pertama" in doc_a

    def test_loads_real_data_files(self, real_data_dir):
        """Smoke test: loads the actual 3 RAG files from data/."""
        docs = load_documents(real_data_dir)
        assert len(docs) == 3
        filenames = [name for name, _ in docs]
        assert "RAG_Direktori_Asuransi.txt" in filenames
        assert "RAG_FAQ_Fasilitas_RS.txt" in filenames
        assert "RAG_SOP_BPJS_Rujukan.txt" in filenames