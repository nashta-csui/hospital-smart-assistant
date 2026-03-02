from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.base.base_model import Base
from app.models.base.dokter import Dokter
from app.config import settings
from app.schemas.dokter import DokterRegisterRequest, DokterRegisterResponse
from app.repositories.dokter_repository import SQLAlchemyDokterRepository
from app.services.dokter_service import DokterRegistrationService, PasswordService
from app.exceptions import DuplicateEmailError, InvalidPasswordError, DatabaseError

# Membuat engine SQLAlchemy untuk berkomunikasi dengan DB
# Gunakan engine ini untuk membuat query
engine = create_engine(settings.database_url)


# Dependency injection untuk database session
def get_db():
    """Dependency untuk mendapatkan database session."""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


# Dependency injection untuk services
def get_password_service():
    """Dependency untuk PasswordService."""
    return PasswordService()

def get_dokter_registration_service(
    db: Session = Depends(get_db),
    password_service: PasswordService = Depends(get_password_service)
):
    """Dependency untuk DokterRegistrationService."""
    repository = SQLAlchemyDokterRepository(db)
    return DokterRegistrationService(repository, password_service)


def verify_admin(authorization: str | None = Header(None)) -> str:
    """
    Dependency untuk verify bahwa request berasal dari admin.
    Menerima Authorization header dengan format: "Bearer <token>"
    
    Raises:
        HTTPException: Jika authorization header tidak valid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header diperlukan"
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use: Bearer <token>"
        )

    token = parts[1]
    # Simple validation: untuk sekarang, token tidak boleh kosong
    # Bisa diganti dengan database lookup nanti
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token tidak valid"
        )

    return token


# Kode setup yang dipanggil sebelum aplikasi berjalan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Memastikan bahwa database memiliki setiap tabel yang didefinisikan
    # WARNING: Metadata.create_all() tidak melakukan update skema apabila tabel sudah ada di DB
    Base.metadata.create_all(engine)

    yield


app = FastAPI(lifespan=lifespan)


@app.post(
    "/dokter/register",
    response_model=DokterRegisterResponse,
    status_code=201,
    summary="Register Doctor",
    description="Admin mendaftarkan dokter baru dalam sistem"
)
async def register_dokter(
    request: DokterRegisterRequest,
    service: DokterRegistrationService = Depends(get_dokter_registration_service),
    admin_token: str = Depends(verify_admin)
):
    """
    Endpoint untuk mendaftarkan dokter baru (HANYA ADMIN).

    **Auth:**
    - Requires Authorization header: `Authorization: Bearer <admin_token>`

    **Request:**
    - `nama`: Nama lengkap dokter (3-255 karakter)
    - `email`: Email unik dokter
    - `no_telepon`: Nomor telepon (10-20 digit)
    - `password`: Password minimal 8 karakter
    - `spesialisasi`: Spesialisasi dokter (2-255 karakter)

    **Response (201 Created):**
    - Dokter yang telah terdaftar dengan ID, tanpa password

    **Error Responses:**
    - `401`: Unauthorized (missing atau invalid authorization)
    - `400`: Email sudah terdaftar
    - `422`: Validasi input gagal
    - `500`: Database error
    """
    try:
        dokter = service.register_dokter(request)
        return dokter
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Email sudah terdaftar: {str(e)}"
        )
    except InvalidPasswordError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Password tidak valid: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/")
async def root():
    return {"message": "Hello World"}
