import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from base_model import Base
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# INFO: Diperlukan untuk mencegah circular import dan invalid type saat development
if TYPE_CHECKING:
    from app.models.base.dokter import Dokter
    from app.models.base.sesi_konsultasi import SesiKonsultasi


class JadwalPraktik(Base):
    __tablename__ = "jadwal_praktik"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    """ID dari jadwal praktik"""

    dokter_id: Mapped[UUID] = mapped_column(ForeignKey("dokter.id"))
    """Foreign key yang menunjuk ke dokter dengan jadwal praktik yang bersangkutan"""

    hari_dalam_minggu: Mapped[int]
    """Indeks hari dalam satu minggu, yakni Senin = 1 hingga Minggu = 7"""

    jam_mulai: Mapped[datetime.time]
    """Jam awal dari sesi konsultasi"""

    jam_selesai: Mapped[datetime.time]
    """Jam akhir dari sesi konsultasi"""

    kuota_harian: Mapped[int]
    """Suatu jadwal praktik bisa direservasi lebih dari sekali"""

    is_available: Mapped[bool]
    """Untuk menutup jadwal spesifik (cuti)"""

    # == Relasi dengan tabel lain ==
    dokter: Mapped["Dokter"] = relationship(back_populates="daftar_jadwal_praktik")
    """ID dari dokter yang melayani jadwal praktik ini"""

    daftar_sesi_konsultasi: Mapped[List["SesiKonsultasi"]] = relationship(
        back_populates="jadwal_praktik"
    )
    """Suatu jadwal praktik bisa memiliki lebih dari satu sesi konsultasi"""

    __table_args__ = {
        CheckConstraint(
            "hari_dalam_minggu >= 1 AND hari_dalam_minggu <= 7",
            name="cek_indeks_hari",
        )
    }
