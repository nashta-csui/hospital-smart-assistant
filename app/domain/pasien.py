from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class Pasien(BaseModel):
    id_pasien: str
    nomor_rekam_medis: str
    nik: str
    nama: str
    no_telepon: str
    jenis_kelamin: str
    tanggal_lahir: date
    alamat: str
    email: str
    golongan_darah: str
    password_hash: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None