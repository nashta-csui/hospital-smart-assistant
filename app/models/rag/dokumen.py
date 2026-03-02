import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base.base_model import Base

if TYPE_CHECKING:
    from app.models.rag.chunk_dokumen import ChunkDokumen


class Dokumen(Base):
    __tablename__ = "dokumen"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    filename: Mapped[str]
    """Nama file dengan file extension"""

    rawtext: Mapped[str]
    """Konten dari dokumen dalam bentuk plaintext"""

    uploaded_at: Mapped[datetime.datetime]
    """Waktu dan tanggal dokumen diunggah ke database"""

    # == Relasi dengan tabel lain ==
    daftar_chunk_dokumen: Mapped["ChunkDokumen"] = relationship(
        back_populates="dokumen"
    )
    """Daftar chunk hasil chunking dari dokumen ini"""
