from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class DokterRegisterRequest(BaseModel):
    """
    Schema untuk request registrasi dokter.
    Memvalidasi input dari client sebelum diproses oleh service layer.
    """

    nama: str = Field(
        min_length=3,
        max_length=255,
        description="Nama lengkap dokter; minimal 3 karakter, maksimal 255"
    )
    email: EmailStr = Field(
        description="Email dokter yang unik dalam sistem"
    )
    no_telepon: str = Field(
        min_length=10,
        max_length=20,
        description="Nomor telepon dokter; 10-20 digit"
    )
    password: str = Field(
        min_length=8,
        description="Password dokter; minimal 8 karakter"
    )
    spesialisasi: str = Field(
        min_length=2,
        max_length=255,
        description="Spesialisasi dokter; e.g. 'Kardiologi, Bedah Umum'"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nama": "Dr. Budi Santoso",
                "email": "budi@hospital.com",
                "no_telepon": "081234567890",
                "password": "SecurePass123!",
                "spesialisasi": "Kardiologi"
            }
        }
    )


class DokterRegisterResponse(BaseModel):
    """
    Schema untuk response ketika dokter berhasil terdaftar.
    Hanya mengembalikan informasi publik, bukan password hash.
    """

    id: UUID
    nama: str
    email: str
    no_telepon: str
    spesialisasi: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DokterDetailResponse(BaseModel):
    """
    Schema untuk response detail dokter (untuk GET endpoint).
    Subset dari registrasi response untuk fleksibilitas.
    """

    id: UUID
    nama: str
    email: str
    no_telepon: str
    spesialisasi: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
