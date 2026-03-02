import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.models.base.base_model import Base
from app.repositories.dokter_repository import SQLAlchemyDokterRepository
from app.services.dokter_service import PasswordService, DokterRegistrationService


# Use in-memory SQLite database untuk testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database untuk setiap test function.
    Menggunakan in-memory SQLite untuk fast testing tanpa side effects.
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def dokter_repository(test_db: Session):
    """Fixture untuk dokter repository dengan test database."""
    return SQLAlchemyDokterRepository(test_db)


@pytest.fixture
def password_service():
    """Fixture untuk password service."""
    return PasswordService()


@pytest.fixture
def dokter_registration_service(
    dokter_repository: SQLAlchemyDokterRepository,
    password_service: PasswordService
):
    """Fixture untuk dokter registration service."""
    return DokterRegistrationService(dokter_repository, password_service)


@pytest.fixture
def test_client(test_db: Session):
    """
    Fixture untuk TestClient dengan test database.
    Override the dependency untuk get_db agar menggunakan test database.
    """
    from app.main import app, get_db
    
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()
