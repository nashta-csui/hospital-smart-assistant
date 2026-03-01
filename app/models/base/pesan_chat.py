import datetime
import enum
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base.base_model import Base

# INFO: Diperlukan untuk mencegah circular import dan invalid type saat development
if TYPE_CHECKING:
    from models.base.sesi_chat import SesiChat


class SenderType(enum.Enum):
    USER = "USER"
    AI = "AI"
    SYSTEM = "SYSTEM"


class PesanChat(Base):
    __tablename__ = "pesan_chat"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    sesi_id: Mapped[UUID] = mapped_column(ForeignKey("sesi_chat.id"))
    """Sesi chaat yang mengandung pesan chat ini"""

    sender_type: Mapped[SenderType] = mapped_column(Enum(SenderType))
    """Enum jenis pengirim pesan, yakni USER, AI, dan SENDER"""

    # TODO: Pastikan dengan klien apakah pesan chat disimpan secara plaintext (merujuk pada NFR-01 klien)
    # WARNING: Keep in mind kalau pesan chat dapat di-trace ke sesi chat, yang dapat di-trace ke pasien
    konten_pesan: Mapped[str] = mapped_column(Text)
    """Konten pesan yang disimpan secara plaintext"""

    # INFO: Nama field ini tidak sesuai dengan ERD karena SQLAlchemy memiliki class variable dengan nama yang sama
    metadata_pesan: Mapped[dict[str, Any]]
    """Metadata tambahan pesan yang dapat dihasilkan dan digunakan oleh LLM untuk mencantumkan berkas referensi atau sumber"""

    timestamp: Mapped[datetime.datetime]
    """Waktu pesan dikirim dengan arbitrary precision (disesuaikan dengan logika backend)"""

    # == Relasi dengan tabel lain ==
    sesi_chat: Mapped["SesiChat"] = relationship(back_populates="daftar_pesan_chat")
    """Sesi chat yang mengandung pesan chat ini (1 sesi chat <-> 0..n pesan chat)"""
