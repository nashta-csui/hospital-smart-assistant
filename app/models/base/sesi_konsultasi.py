import datetime
import enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base.base_model import Base

# INFO: Diperlukan untuk mencegah circular import dan invalid type saat development
if TYPE_CHECKING:
    from app.models.base.jadwal_praktik import JadwalPraktik
    from app.models.base.pasien import Pasien
    from app.models.base.sesi_chat import SesiChat


class StatusSesiKonsultasi(enum.Enum):
    BOOKED = 1
    CANCELLED = 2
    COMPLETED = 3


class SesiKonsultasi(Base):
    __tablename__ = "sesi_konsultasi"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    pasien_id: Mapped[UUID] = mapped_column(ForeignKey("pasien.id"))
    """Pasien yang mereservasi sesi konsultasi ini"""

    jadwal_id: Mapped[UUID] = mapped_column(ForeignKey("jadwal_praktik.id"))
    """Jadwal praktik yang mengandung sesi konsultasi ini"""

    sesi_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("sesi_chat.id"), unique=True, nullable=True
    )
    """Sesi chat yang menghasilkan sesi konsultasi ini (bisa jadi tidak ada)"""

    tanggal_kunjungan: Mapped[datetime.date]
    """Tanggal kunjungan pasien untuk sesi konsultasi"""

    # TODO: Tentukan cara generate nomor antrean secara otomatis
    # TODO: Tentukan constraint dari nomor_antrean (e.g. unique per jadwal_praktik atau per tanggal_kunjungan)
    # INFO: Komentar di bawah merupakan contoh constraint unique yang dapat ditambahkan
    # __table_args__ = {
    #   UniqueConstraint("nomor_antrean", "tanggal_kunjungan", name="uq_jadwal_tanggal")
    # }
    nomor_antrean: Mapped[str]
    """Nomor antrean yang di-generate secara otomatis oleh sistem"""

    # TODO: Konfirmasi apakah keluhan pasien di-proses oleh LLM terlebih dahulu
    keluhan: Mapped[str] = mapped_column(Text)
    """Keluhan pasien setelah diproses oleh LLM"""

    status: Mapped[StatusSesiKonsultasi] = mapped_column(Enum(StatusSesiKonsultasi))
    """Status dari sesi konsultasi, yakni BOOKED = 1, CANCELLED = 2, dan COMPLETE = 3"""

    created_at: Mapped[datetime.datetime]
    """Waktu sesi konsultasi dibuat, baik secara manual oleh staf administrasi atau smart assistant"""

    # == Relasi dengan tabel lain ==
    pasien: Mapped["Pasien"] = relationship(back_populates="daftar_sesi_konsultasi")
    """Pasien yang terlibat dengan sesi konsultasi (1 pasien <-> 0..n sesi konsultasi)"""

    jadwal_praktik: Mapped["JadwalPraktik"] = relationship(
        back_populates="daftar_sesi_konsultasi"
    )
    """Jadwal praktik yang mengandung sesi konsultasi ini (1 jadwal praktik <-> 0..n sesi konsultasi)"""

    sesi_chat: Mapped[Optional["SesiChat"]] = relationship(
        back_populates="sesi_konsultasi"
    )
    """Sesi chat yang menghasilkan sesi konsultasi yang bersangkutan (1 sesi chat <-> 0..1 sesi konsultasi)"""
