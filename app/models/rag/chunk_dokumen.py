from typing import List
from uuid import UUID

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base.base_model import Base
from app.models.rag.consts import EMBEDDING_DIMS
from app.models.rag.dokumen import Dokumen


class ChunkDokumen(Base):
    """
    ChunkDokumen yang dapat di-index berdasarkan HNSW dengan
    metrik kedekatan L2 (euclidean) distance

    Berikut adalah contoh query yang dapat dibuat:
    ```
    from sqlalchemy import select

    stmt = select(ChunkDokumen).order_by(
        ChunkDokumen.embedding.l2_distance(query_embedding)
    ).limit(5)
    ```
    """

    id: Mapped[UUID] = mapped_column(primary_key=True)

    doc_id: Mapped[UUID] = mapped_column(ForeignKey("dokumen.id"))
    """ID dari dokumen sumber chunk dokumen ini"""

    content: Mapped[str] = mapped_column(Text)
    """Konten dari chunk ini, yang digunakan oleh LLM sebagai konteks tambahan"""

    embedding: Mapped[List[float]] = mapped_column(VECTOR(EMBEDDING_DIMS))
    """Embedding dari chunk ini agar dapat di-fetch oleh sistem RAG"""

    # == Relasi dengan tabel lain ==
    dokumen: Mapped["Dokumen"] = relationship(back_populates="daftar_chunk_dokumen")
    """Dokumen sumber chunk dokumen ini"""

    __table_args__ = {
        Index(
            "embedding_index",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_l2_ops"},
        )
    }
    """Index embedding dibuat agar retrieval objek ChunkDokumen dengan embedding paling sesuai dengan query dapat ditemukan dengan cepat"""
