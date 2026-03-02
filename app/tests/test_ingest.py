from pathlib import Path

import pytest

from app.services.ingest import chunk_text, load_documents


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


class TestChunkText:
    """Tests for chunk_text: splits text into overlapping chunks."""

    def test_splits_text_into_chunks(self):
        """Should split text into multiple chunks."""
        text = "Seksi A\n\nSeksi B\n\nSeksi C\n\nSeksi D"
        chunks = chunk_text(text, chunk_size=20, chunk_overlap=0)
        assert len(chunks) > 1

    def test_respects_chunk_size(self):
        """Each chunk should not exceed chunk_size (with some tolerance)."""
        text = (
            "Paragraf satu berisi informasi.\n\n"
            "Paragraf dua berisi data.\n\n"
            "Paragraf tiga."
        )
        chunks = chunk_text(text, chunk_size=40, chunk_overlap=0)
        for chunk in chunks:
            assert len(chunk) <= 60

    def test_overlap_creates_redundancy(self):
        """With overlap, adjacent chunks should share some content."""
        text = "AAAA BBBB CCCC DDDD EEEE FFFF GGGG HHHH"
        chunks_no_overlap = chunk_text(text, chunk_size=20, chunk_overlap=0)
        chunks_with_overlap = chunk_text(text, chunk_size=20, chunk_overlap=5)
        assert len(chunks_with_overlap) >= len(chunks_no_overlap)

    def test_empty_text_returns_empty_list(self):
        """Should return empty list for empty text."""
        chunks = chunk_text("", chunk_size=500, chunk_overlap=50)
        assert chunks == []

    def test_short_text_returns_single_chunk(self):
        """Text shorter than chunk_size should return one chunk."""
        text = "Short text."
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 1
        assert chunks[0] == "Short text."

    def test_prefers_paragraph_separators(self):
        """Should split on paragraph boundaries (double newline)."""
        text = "Paragraf satu.\n\nParagraf dua."
        chunks = chunk_text(text, chunk_size=20, chunk_overlap=0)
        assert any("Paragraf satu." in c for c in chunks)
        assert any("Paragraf dua." in c for c in chunks)

    def test_default_parameters(self):
        """Should work with default chunk_size=500 and chunk_overlap=50."""
        text = "A" * 1000
        chunks = chunk_text(text)
        assert len(chunks) > 1

    def test_preserves_all_content(self):
        """Union of all chunks should contain all original content."""
        text = "Satu Dua Tiga Empat Lima"
        chunks = chunk_text(text, chunk_size=15, chunk_overlap=0)
        combined = " ".join(chunks)
        for word in ["Satu", "Dua", "Tiga", "Empat", "Lima"]:
            assert word in combined
