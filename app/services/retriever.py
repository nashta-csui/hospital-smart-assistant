from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rag.chunk_dokumen import ChunkDokumen
from app.services import get_embedding_model


def retrieve_chunks(
    db: Session, query: str, top_k: int = 4
) -> list[ChunkDokumen]:
    """
    Embed a query and find the closest document chunks via pgvector L2 distance.

    Returns up to top_k ChunkDokumen records ordered by similarity.
    """
    model = get_embedding_model()
    query_embedding = model.encode(query).tolist()

    stmt = (
        select(ChunkDokumen)
        .order_by(ChunkDokumen.embedding.l2_distance(query_embedding))
        .limit(top_k)
    )
    return list(db.scalars(stmt).all())
