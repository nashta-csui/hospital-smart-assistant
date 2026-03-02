from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base.base_model import Base, Email, NomorTelepon

# INFO: Diperlukan untuk mencegah circular import dan invalid type saat development
if TYPE_CHECKING:
    from app.models.base.jadwal_praktik import JadwalPraktik


class Dokter(Base):
    __tablename__ = "dokter"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    """ID dokter dalam format UUID v4"""

    nama: Mapped[str] = mapped_column(String(255))
    """Nama lengkap dokter"""

    no_telepon: Mapped[NomorTelepon]
    """Nomor telepon dokter yang dapat dihubungi oleh pasien"""

    email: Mapped[Email] = mapped_column(unique=True)
    """Email dokter yang dapat dihubungi oleh pasien"""

    password_hash: Mapped[str]
    """Hash Argon2 dari password login yang digunakan oleh dokter"""

    # TODO: Pastikan spesialisasi dapat di-fuzzy search sesuai SDS
    spesialisasi: Mapped[str] = mapped_column()
    """Spesialisasi dokter; bisa lebih dari satu (comma separated)"""

    is_active: Mapped[bool]
    """Indikator keaktifan dokter dalam melayani pasien"""

    # == Relasi dengan tabel lain ==
    daftar_jadwal_praktik: Mapped[List["JadwalPraktik"]] = relationship(
        back_populates="dokter"
    )
    """Daftar jadwal praktik dokter yang tersedia (1 dokter <-> 0..n jadwal praktik)"""
