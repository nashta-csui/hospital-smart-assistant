from unittest.mock import MagicMock, patch

from app.services.retriever import retrieve_chunks


class TestRetrieveChunks:
    """Tests for retrieve_chunks with mocked embedding model and DB session."""

    @patch("app.services.retriever.get_embedding_model")
    def test_encodes_query_string(self, mock_get_model, mock_embedding_model):
        """Should encode the query string using the embedding model."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()
        session.scalars.return_value.all.return_value = []

        retrieve_chunks(session, "test query")

        mock_embedding_model.encode.assert_called_once_with("test query")

    @patch("app.services.retriever.get_embedding_model")
    def test_returns_results_from_db(self, mock_get_model, mock_embedding_model):
        """Should return whatever the DB query returns."""
        mock_get_model.return_value = mock_embedding_model
        fake_chunk = MagicMock()
        session = MagicMock()
        session.scalars.return_value.all.return_value = [fake_chunk]

        results = retrieve_chunks(session, "query")
        assert results == [fake_chunk]

    @patch("app.services.retriever.get_embedding_model")
    def test_queries_database(self, mock_get_model, mock_embedding_model):
        """Should call db.scalars() to execute the query."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()
        session.scalars.return_value.all.return_value = []

        retrieve_chunks(session, "query")
        session.scalars.assert_called_once()

    @patch("app.services.retriever.get_embedding_model")
    def test_empty_results(self, mock_get_model, mock_embedding_model):
        """Should return empty list when DB has no chunks."""
        mock_get_model.return_value = mock_embedding_model
        session = MagicMock()
        session.scalars.return_value.all.return_value = []

        results = retrieve_chunks(session, "nonexistent")
        assert results == []

    @patch("app.services.retriever.get_embedding_model")
    def test_returns_multiple_results(self, mock_get_model, mock_embedding_model):
        """Should return multiple chunks when available."""
        mock_get_model.return_value = mock_embedding_model
        fake_chunks = [MagicMock(), MagicMock(), MagicMock()]
        session = MagicMock()
        session.scalars.return_value.all.return_value = fake_chunks

        results = retrieve_chunks(session, "query", top_k=3)
        assert len(results) == 3
