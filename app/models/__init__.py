# Model ini di-import oleh alembic/env.py untuk memungkinkan
# autogeneration migrasi
from app.models.base.base_model import Base

from app.models.base.admin import Admin
from app.models.base.dokter import Dokter
from app.models.base.jadwal_praktik import JadwalPraktik
from app.models.base.pasien import Pasien
from app.models.base.pesan_chat import PesanChat
from app.models.base.sesi_chat import SesiChat
from app.models.base.sesi_konsultasi import SesiKonsultasi
from app.models.rag.chunk_dokumen import ChunkDokumen
from app.models.rag.dokumen import Dokumen
