import pytest
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from app.schemas.dokter import DokterRegisterRequest
from app.repositories.dokter_repository import DokterRepository, SQLAlchemyDokterRepository
from app.services.dokter_service import DokterRegistrationService, PasswordService
from app.exceptions import DuplicateEmailError, InvalidPasswordError, DatabaseError
from app.models.base.dokter import Dokter


class TestPasswordService:
    """Test cases untuk PasswordService - utility layer."""

    def test_hash_password_should_return_hashed_string(self):
        """Positive: Password hashing harus menghasilkan string yang berbeda dari password asli."""
        # Arrange
        service = PasswordService()
        password = "SecurePassword123!"

        # Act
        hashed = service.hash_password(password)

        # Assert
        assert hashed != password
        assert len(hashed) > len(password)
        assert "$argon2" in hashed  # Argon2 hash format

    def test_hash_password_should_be_deterministic_but_different(self):
        """Positive: Setiap hashing menghasilkan hash berbeda (salted), tapi password sama valid."""
        # Arrange
        service = PasswordService()
        password = "SecurePassword123!"

        # Act
        hash1 = service.hash_password(password)
        hash2 = service.hash_password(password)

        # Assert
        assert hash1 != hash2  # Berbeda karena berbeda salt
        assert service.verify_password(password, hash1)  # Tapi keduanya valid
        assert service.verify_password(password, hash2)

    def test_verify_password_should_return_true_for_correct_password(self):
        """Positive: Verification harus return True untuk password yang benar."""
        # Arrange
        service = PasswordService()
        password = "SecurePassword123!"
        hashed = service.hash_password(password)

        # Act
        result = service.verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_should_return_false_for_incorrect_password(self):
        """Negative: Verification harus return False untuk password yang salah."""
        # Arrange
        service = PasswordService()
        password = "SecurePassword123!"
        hashed = service.hash_password(password)

        # Act
        result = service.verify_password("WrongPassword456!", hashed)

        # Assert
        assert result is False

    def test_verify_password_should_return_false_for_empty_password(self):
        """Negative: Verification harus handle empty password dengan aman."""
        # Arrange
        service = PasswordService()
        hashed = service.hash_password("SecurePassword123!")

        # Act
        result = service.verify_password("", hashed)

        # Assert
        assert result is False


class TestDokterRegistrationService:
    """Test cases untuk DokterRegistrationService - business logic layer."""

    @pytest.fixture
    def mock_repository(self):
        """Mock repository untuk testing."""
        return Mock(spec=DokterRepository)

    def test_register_dokter_should_successfully_create_dokter(
        self,
        dokter_registration_service: DokterRegistrationService
    ):
        """Positive: Registrasi dokter dengan data valid harus sukses."""
        # Arrange
        request = DokterRegisterRequest(
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password="SecurePass123!",
            spesialisasi="Kardiologi"
        )

        # Act
        result = dokter_registration_service.register_dokter(request)

        # Assert
        assert result is not None
        assert result.nama == request.nama
        assert result.email == request.email
        assert result.no_telepon == request.no_telepon
        assert result.spesialisasi == request.spesialisasi
        assert result.is_active is True
        assert result.password_hash != request.password  # Password harus di-hash
        assert result.id is not None

    def test_register_dokter_should_reject_duplicate_email(
        self,
        dokter_registration_service: DokterRegistrationService,
        password_service: PasswordService,
        test_db: Session
    ):
        """Negative: Registrasi dengan email yang sudah ada harus reject."""
        # Arrange - register dokter pertama
        request1 = DokterRegisterRequest(
            nama="Dr. Budi Santoso",
            email="existing@hospital.com",
            no_telepon="081234567890",
            password="SecurePass123!",
            spesialisasi="Kardiologi"
        )
        dokter_registration_service.register_dokter(request1)

        # Act - coba register dengan email yang sama
        request2 = DokterRegisterRequest(
            nama="Dr. Andi Wijaya",
            email="existing@hospital.com",  # Email sama
            no_telepon="089876543210",
            password="AnotherPass456!",
            spesialisasi="Urologi"
        )

        # Assert
        with pytest.raises(DuplicateEmailError) as exc_info:
            dokter_registration_service.register_dokter(request2)
        assert "sudah terdaftar" in str(exc_info.value)

    def test_register_dokter_should_hash_password_securely(
        self,
        dokter_registration_service: DokterRegistrationService
    ):
        """Positive: Password harus di-hash sebelum disimpan."""
        # Arrange
        plain_password = "SecurePass123!"
        request = DokterRegisterRequest(
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password=plain_password,
            spesialisasi="Kardiologi"
        )

        # Act
        result = dokter_registration_service.register_dokter(request)

        # Assert
        assert result.password_hash != plain_password
        assert "$argon2" in result.password_hash

    def test_register_dokter_should_set_is_active_default_true(
        self,
        dokter_registration_service: DokterRegistrationService
    ):
        """Positive: Status aktif dokter baru harus default True."""
        # Arrange
        request = DokterRegisterRequest(
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password="SecurePass123!",
            spesialisasi="Kardiologi"
        )

        # Act
        result = dokter_registration_service.register_dokter(request)

        # Assert
        assert result.is_active is True


class TestDokterRepository:
    """Test cases untuk DokterRepository - database layer."""

    def test_create_dokter_should_save_to_database(
        self,
        dokter_repository: SQLAlchemyDokterRepository,
        password_service: PasswordService
    ):
        """Positive: Create harus simpan dokter ke database."""
        # Arrange
        dokter = Dokter(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password_hash=password_service.hash_password("SecurePass123!"),
            spesialisasi="Kardiologi",
            is_active=True,
        )

        # Act
        result = dokter_repository.create(dokter)

        # Assert
        assert result.id == dokter.id
        assert result.email == dokter.email

    def test_get_by_email_should_retrieve_dokter(
        self,
        dokter_repository: SQLAlchemyDokterRepository,
        password_service: PasswordService
    ):
        """Positive: get_by_email harus return dokter jika ada."""
        # Arrange
        dokter = Dokter(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password_hash=password_service.hash_password("SecurePass123!"),
            spesialisasi="Kardiologi",
            is_active=True
        )
        dokter_repository.create(dokter)

        # Act
        result = dokter_repository.get_by_email("budi@hospital.com")

        # Assert
        assert result is not None
        assert result.email == "budi@hospital.com"
        assert result.nama == "Dr. Budi Santoso"

    def test_get_by_email_should_return_none_if_not_found(
        self,
        dokter_repository: SQLAlchemyDokterRepository
    ):
        """Negative: get_by_email harus return None jika email tidak ada."""
        # Act
        result = dokter_repository.get_by_email("nonexistent@hospital.com")

        # Assert
        assert result is None

    def test_get_by_id_should_retrieve_dokter(
        self,
        dokter_repository: SQLAlchemyDokterRepository,
        password_service: PasswordService
    ):
        """Positive: get_by_id harus return dokter jika ada."""
        # Arrange
        dokter_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        dokter = Dokter(
            id=dokter_id,
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password_hash=password_service.hash_password("SecurePass123!"),
            spesialisasi="Kardiologi",
            is_active=True
        )
        dokter_repository.create(dokter)

        # Act
        result = dokter_repository.get_by_id(dokter_id)

        # Assert
        assert result is not None
        assert result.id == dokter_id

    def test_get_by_id_should_return_none_if_not_found(
        self,
        dokter_repository: SQLAlchemyDokterRepository
    ):
        """Negative: get_by_id harus return None jika ID tidak ada."""
        # Act
        result = dokter_repository.get_by_id(
            UUID("550e8400-e29b-41d4-a716-446655440000")
        )

        # Assert
        assert result is None

    def test_exists_by_email_should_return_true_if_email_exists(
        self,
        dokter_repository: SQLAlchemyDokterRepository,
        password_service: PasswordService
    ):
        """Positive: exists_by_email harus return True jika email ada."""
        # Arrange
        dokter = Dokter(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password_hash=password_service.hash_password("SecurePass123!"),
            spesialisasi="Kardiologi",
            is_active=True
        )
        dokter_repository.create(dokter)

        # Act
        result = dokter_repository.exists_by_email("budi@hospital.com")

        # Assert
        assert result is True

    def test_exists_by_email_should_return_false_if_email_not_exists(
        self,
        dokter_repository: SQLAlchemyDokterRepository
    ):
        """Negative: exists_by_email harus return False jika email tidak ada."""
        # Act
        result = dokter_repository.exists_by_email("nonexistent@hospital.com")

        # Assert
        assert result is False

    def test_create_with_duplicate_email_should_raise_error(
        self,
        dokter_repository: SQLAlchemyDokterRepository,
        password_service: PasswordService
    ):
        """Negative: Create dengan email duplikat harus raise DuplicateEmailError."""
        # Arrange
        dokter1 = Dokter(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            nama="Dr. Budi Santoso",
            email="budi@hospital.com",
            no_telepon="081234567890",
            password_hash=password_service.hash_password("SecurePass123!"),
            spesialisasi="Kardiologi",
            is_active=True
        )
        dokter_repository.create(dokter1)

        dokter2 = Dokter(
            id=UUID("550e8400-e29b-41d4-a716-446655440001"),
            nama="Dr. Andi Wijaya",
            email="budi@hospital.com",  # Email sama
            no_telepon="089876543210",
            password_hash=password_service.hash_password("AnotherPass456!"),
            spesialisasi="Urologi",
            is_active=True
        )

        # Act & Assert
        with pytest.raises(DuplicateEmailError):
            dokter_repository.create(dokter2)

