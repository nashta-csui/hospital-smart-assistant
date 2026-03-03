import pytest
import datetime
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.models.base.base_model import Base
from app.models.base.dokter import Dokter
from app.models.base.admin import Admin
from app.models.base.pasien import Pasien, JenisKelamin
from app.repositories.dokter_repository import SQLAlchemyDokterRepository
from app.services.dokter_service import PasswordService, DokterRegistrationService


# Konstanta test data
VALID_PASSWORD = "SecurePass123!"
DOKTER_EMAIL   = "dokter@hospital.com"
ADMIN_EMAIL    = "admin@hospital.com"
PASIEN_EMAIL   = "pasien@hospital.com"
INACTIVE_EMAIL = "inactive@hospital.com"

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# CORE FIXTURES (Database & Client)

@pytest.fixture(scope="function")
def test_db():
    """
    Buat test database in-memory SQLite untuk setiap test function.
    StaticPool memastikan semua session pakai koneksi yang sama.
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_client(test_db: Session):
    """
    TestClient dengan test database.
    Override dependency get_db agar pakai test database.
    """
    from app.main import app, get_db

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


# DOKTER REGISTRATION FIXTURES

@pytest.fixture
def dokter_repository(test_db: Session):
    """Fixture untuk dokter repository dengan test database."""
    return SQLAlchemyDokterRepository(test_db)


@pytest.fixture
def password_service():
    """Fixture untuk PasswordService."""
    return PasswordService()


@pytest.fixture
def dokter_registration_service(
    dokter_repository: SQLAlchemyDokterRepository,
    password_service: PasswordService
):
    """Fixture untuk DokterRegistrationService."""
    return DokterRegistrationService(dokter_repository, password_service)


# AUTH FIXTURES

@pytest.fixture
def auth_repository(test_db: Session):
    """Fixture untuk auth repository dengan test database."""
    from app.repositories.auth_repository import SQLAlchemyAuthRepository
    return SQLAlchemyAuthRepository(test_db)


@pytest.fixture
def token_service():
    """Fixture untuk TokenService."""
    from app.services.auth_service import TokenService
    return TokenService()


@pytest.fixture
def auth_service(auth_repository, password_service, token_service):
    """Fixture untuk AuthService dengan semua dependencies."""
    from app.services.auth_service import AuthService
    return AuthService(auth_repository, password_service, token_service)

# SEEDED DATA FIXTURES

@pytest.fixture
def seeded_dokter(test_db: Session, password_service: PasswordService):
    """Fixture: Dokter aktif yang sudah ada di database."""
    dokter = Dokter(
        id=uuid4(),
        nama="Dr. Test Aktif",
        email=DOKTER_EMAIL,
        no_telepon="081234567890",
        password_hash=password_service.hash_password(VALID_PASSWORD),
        spesialisasi="Umum",
        is_active=True,
    )
    test_db.add(dokter)
    test_db.commit()
    return dokter


@pytest.fixture
def seeded_inactive_dokter(test_db: Session, password_service: PasswordService):
    """Fixture: Dokter TIDAK aktif yang sudah ada di database."""
    dokter = Dokter(
        id=uuid4(),
        nama="Dr. Test Nonaktif",
        email=INACTIVE_EMAIL,
        no_telepon="089999999999",
        password_hash=password_service.hash_password(VALID_PASSWORD),
        spesialisasi="Umum",
        is_active=False,
    )
    test_db.add(dokter)
    test_db.commit()
    return dokter


@pytest.fixture
def seeded_admin(test_db: Session, password_service: PasswordService):
    """Fixture: Admin yang sudah ada di database."""
    admin = Admin(
        id=uuid4(),
        nama="Admin Test",
        email=ADMIN_EMAIL,
        password_hash=password_service.hash_password(VALID_PASSWORD),
    )
    test_db.add(admin)
    test_db.commit()
    return admin


@pytest.fixture
def seeded_pasien(test_db: Session, password_service: PasswordService):
    """Fixture: Pasien yang sudah ada di database."""
    pasien = Pasien(
        id=uuid4(),
        nomor_rekam_medis="RM-TEST-001",
        nik="1234567890123456",
        nama="Pasien Test",
        no_telepon="081111111111",
        jenis_kelamin=JenisKelamin.L,
        tanggal_lahir=datetime.date(1990, 1, 1),
        alamat="Jalan Test No. 1",
        email=PASIEN_EMAIL,
        password_hash=password_service.hash_password(VALID_PASSWORD),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    test_db.add(pasien)
    test_db.commit()
    return pasien
