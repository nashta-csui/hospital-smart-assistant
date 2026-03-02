import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base.base_model import Base

# INFO: Diperlukan untuk mencegah circular import dan invalid type saat development
if TYPE_CHECKING:
    from app.models.base.pasien import Pasien
    from app.models.base.pesan_chat import PesanChat
    from app.models.base.sesi_konsultasi import SesiKonsultasi


class SesiChat(Base):
    __tablename__ = "sesi_chat"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    pasien_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("pasien.id"))
    """Pasien yang terlibat dalam sesi chat; bisa bernilai NULL untuk Guest Mode (0..1 pasien <-> 0..n sesi chat)"""

    # TODO: Konkretkan business definition untuk waktu_mulai
    waktu_mulai: Mapped[datetime.datetime]
    """Waktu sesi chat dimulai, dihitung dari pengiriman pesan pertama oleh pasien"""

    # TODO: Konkretkan business definition untuk waktu_selesai
    waktu_selesai: Mapped[datetime.datetime]
    """Waktu sesi chat selesai, dihitung saat ???"""

    summary_topik: Mapped[str] = mapped_column(String(100))
    """Topik percakapan (sekitar 2-5 kata) menurut LLM; digunakan untuk monitoring jenis query yang paling sering dibuat oleh pengguna"""

    # == Relasi dengan tabel lain ==
    sesi_konsultasi: Mapped[Optional["SesiKonsultasi"]] = relationship(
        back_populates="sesi_chat"
    )
    """Sesi konsultasi yang diciptakan berdasarkan sesi chat ini (1 sesi chat <-> 0..1 sesi konsultasi)"""

    daftar_pesan_chat: Mapped[List["PesanChat"]] = relationship(
        back_populates="sesi_chat"
    )
    """Daftar pesan chat yang dibuat pada sesi chat ini (1 sesi chat <-> 0..n pesan chat"""

    pasien: Mapped[Optional["Pasien"]] = relationship(back_populates="daftar_sesi_chat")
    """Pasien yang terlibat dalam sesi chat (0..1 pasien <-> 0..n sesi chat)"""
