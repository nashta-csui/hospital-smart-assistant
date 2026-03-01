import datetime
import enum
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base.base_model import Base, Email, NomorTelepon

# INFO: Diperlukan untuk mencegah circular import dan invalid type saat development
if TYPE_CHECKING:
    from app.models.base.sesi_chat import SesiChat
    from app.models.base.sesi_konsultasi import SesiKonsultasi


class JenisKelamin(enum.Enum):
    L = 1
    P = 2


class Pasien(Base):
    __tablename__ = "pasien"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    """ID dari pasien pada sistem smart hospital, terpisah dari logika internal rumah sakit"""

    nomor_rekam_medis: Mapped[str] = mapped_column(unique=True)
    """Nomor rekam medis sesuai dengan ketentuan rumah sakit"""

    # TODO: Pastikan data dienkripsi menggunakan AES-256 at rest
    nik: Mapped[str] = mapped_column(String(16), unique=True)
    """NIK pasien yang dienkripsi menggunakan AES-256"""

    nama: Mapped[str] = mapped_column(String(255))
    """Nama lengkap pasien"""

    # TODO: Pastikan nomor telepon terenkripsi AES-256 at rest
    no_telepon: Mapped[NomorTelepon]
    """Nomor telepon pasien yang dapat dihubungi; dienkripsi menggunakan AES-256"""

    jenis_kelamin: Mapped[JenisKelamin] = mapped_column(Enum(JenisKelamin))
    """Jenis kelamin pasien; L = lelaki, P = perempuan"""

    tanggal_lahir: Mapped[datetime.date]
    """Tanggal lahir pasien"""

    alamat: Mapped[str] = mapped_column(Text)
    """Alamat lengkap pasien"""

    email: Mapped[Email] = mapped_column(unique=True)
    """Alamat aktif pasien; unik untuk setiap akun"""

    password_hash: Mapped[str]
    """Password akun pasien yang sudah di-hash menggunakan algoritma Argon2"""

    created_at: Mapped[datetime.datetime]
    """Waktu dan tanggal pembuatan akun pasien"""

    updated_at: Mapped[datetime.datetime]
    """Waktu dan tanggal perubahan terakhir pada akun pasien"""

    # == Relasi dengan tabel lain ==
    daftar_sesi_konsultasi: Mapped[List["SesiKonsultasi"]] = relationship(
        back_populates="pasien"
    )
    """Daftar sesi konsultasi yang pernah direservasi oleh pasien (1 pasien <-> 0..n sesi konsultasi)"""

    daftar_sesi_chat: Mapped[List["SesiChat"]] = relationship(back_populates="pasien")
    """Daftar sesi chat yang pernah dibuat oleh pasien (1 pasien <-> 0..n sesi konsultasi)"""
