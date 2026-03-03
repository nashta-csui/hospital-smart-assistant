from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.models.rag.chunk_dokumen import ChunkDokumen
from app.models.rag.consts import EMBEDDING_DIMS, EMBEDDING_MODEL_NAME
from app.models.rag.dokumen import Dokumen
from app.services.ingest import chunk_text, ingest_documents, load_documents


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


class TestGetEmbeddingModel:
    """Tests for get_embedding_model singleton loader."""

    @patch("app.services.SentenceTransformer")
    def test_loads_correct_model(self, mock_st_class):
        """Should load the model specified in EMBEDDING_MODEL_NAME."""
        import app.services

        app.services._embedding_model = None
        app.services.get_embedding_model()
        mock_st_class.assert_called_once_with(EMBEDDING_MODEL_NAME)

    @patch("app.services.SentenceTransformer")
    def test_returns_singleton(self, mock_st_class):
        """Should return the same instance on subsequent calls."""
        import app.services

        app.services._embedding_model = None
        model1 = app.services.get_embedding_model()
        model2 = app.services.get_embedding_model()
        assert model1 is model2
        mock_st_class.assert_called_once()


class TestIngestDocuments:
    """Tests for ingest_documents with mocked embedding model and DB session."""

    @patch("app.services.ingest.get_embedding_model")
    def test_creates_dokumen_for_each_file(
        self, mock_get_model, mock_embedding_model, tmp_data_dir
    ):
        """Should create one Dokumen per RAG file."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        ingest_documents(session, tmp_data_dir)

        added = [call.args[0] for call in session.add.call_args_list]
        dokumens = [obj for obj in added if isinstance(obj, Dokumen)]
        assert len(dokumens) == 2

    @patch("app.services.ingest.get_embedding_model")
    def test_creates_chunk_records_with_embeddings(
        self, mock_get_model, mock_embedding_model, tmp_data_dir
    ):
        """Should create ChunkDokumen records with content and embeddings."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        ingest_documents(session, tmp_data_dir)

        added = [call.args[0] for call in session.add.call_args_list]
        chunks = [obj for obj in added if isinstance(obj, ChunkDokumen)]
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.content
            assert chunk.embedding is not None
            assert len(chunk.embedding) == EMBEDDING_DIMS

    @patch("app.services.ingest.get_embedding_model")
    def test_chunks_linked_to_dokumen(
        self, mock_get_model, mock_embedding_model, tmp_data_dir
    ):
        """Each ChunkDokumen.doc_id should match a Dokumen.id."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        ingest_documents(session, tmp_data_dir)

        added = [call.args[0] for call in session.add.call_args_list]
        dokumens = [obj for obj in added if isinstance(obj, Dokumen)]
        chunks = [obj for obj in added if isinstance(obj, ChunkDokumen)]
        doc_ids = {d.id for d in dokumens}
        for chunk in chunks:
            assert chunk.doc_id in doc_ids

    @patch("app.services.ingest.get_embedding_model")
    def test_calls_encode_with_chunk_texts(
        self, mock_get_model, mock_embedding_model, tmp_data_dir
    ):
        """Should call model.encode() with the chunked text."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        ingest_documents(session, tmp_data_dir)

        assert mock_embedding_model.encode.called
        for call in mock_embedding_model.encode.call_args_list:
            chunks_arg = call.args[0]
            assert isinstance(chunks_arg, list)
            assert all(isinstance(c, str) for c in chunks_arg)

    @patch("app.services.ingest.get_embedding_model")
    def test_stores_rawtext_in_dokumen(
        self, mock_get_model, mock_embedding_model, tmp_data_dir
    ):
        """Dokumen.rawtext should contain the full file content."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        ingest_documents(session, tmp_data_dir)

        added = [call.args[0] for call in session.add.call_args_list]
        dokumens = [obj for obj in added if isinstance(obj, Dokumen)]
        doc_a = next(d for d in dokumens if d.filename == "RAG_File_A.txt")
        assert "konten pertama" in doc_a.rawtext

    @patch("app.services.ingest.get_embedding_model")
    def test_skips_empty_content_file(
        self, mock_get_model, mock_embedding_model, tmp_path
    ):
        """Should skip chunking for files with only whitespace content."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()
        (tmp_path / "RAG_Empty.txt").write_text("   \n\n  ", encoding="utf-8")

        ingest_documents(session, tmp_path)

        added = [call.args[0] for call in session.add.call_args_list]
        dokumens = [obj for obj in added if isinstance(obj, Dokumen)]
        chunks = [obj for obj in added if isinstance(obj, ChunkDokumen)]
        assert len(dokumens) == 1
        assert len(chunks) == 0

    @patch("app.services.ingest.get_embedding_model")
    def test_empty_directory_returns_zero(
        self, mock_get_model, mock_embedding_model, empty_data_dir
    ):
        """Should return 0 and not add anything when no RAG files exist."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        count = ingest_documents(session, empty_data_dir)
        assert count == 0

    @patch("app.services.ingest.get_embedding_model")
    def test_returns_document_count(
        self, mock_get_model, mock_embedding_model, tmp_data_dir
    ):
        """Should return the number of documents ingested."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        count = ingest_documents(session, tmp_data_dir)
        assert count == 2

    @patch("app.services.ingest.get_embedding_model")
    def test_commits_session(
        self, mock_get_model, mock_embedding_model, tmp_data_dir
    ):
        """Should commit the session after ingesting."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()

        ingest_documents(session, tmp_data_dir)
        session.commit.assert_called_once()
