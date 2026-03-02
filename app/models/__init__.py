# Model ini di-import oleh alembic/env.py untuk memungkinkan
# autogeneration migrasi
from app.models.base.base_model import Base as Base

from app.models.base.admin import Admin as Admin
from app.models.base.dokter import Dokter as Dokter
from app.models.base.jadwal_praktik import JadwalPraktik as JadwalPraktik
from app.models.base.pasien import Pasien as Pasien
from app.models.base.pesan_chat import PesanChat as PesanChat
from app.models.base.sesi_chat import SesiChat as SesiChat
from app.models.base.sesi_konsultasi import SesiKonsultasi as SesiKonsultasi
from app.models.rag.chunk_dokumen import ChunkDokumen as ChunkDokumen
from app.models.rag.dokumen import Dokumen as Dokumen
