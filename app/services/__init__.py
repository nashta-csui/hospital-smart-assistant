from sentence_transformers import SentenceTransformer

from app.models.rag.consts import EMBEDDING_MODEL_NAME

_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy-load the shared embedding model singleton."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model
