from pydantic import BaseModel

class Pasien(BaseModel):
    id_pasien: str
    nik: str
    nama: str
    no_telepon: str
    alamat: str
    golongan_darah: str
    password_hash: str
