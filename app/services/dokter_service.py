from uuid import uuid4
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

from app.models.base.dokter import Dokter
from app.repositories.dokter_repository import DokterRepository
from app.exceptions import DuplicateEmailError, InvalidPasswordError
from app.schemas.dokter import DokterRegisterRequest


class PasswordService:
    """
    Service untuk password hashing dan verification.
    Menggunakan Argon2 sebagai hashing algorithm yang aman.
    Single Responsibility: Hanya menangani password operations.
    """

    def __init__(self):
        """Initialize password hasher dengan default parameters."""
        self.hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """
        Hash password menggunakan Argon2.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password

        Raises:
            InvalidPasswordError: Jika hashing fails
        """
        try:
            return self.hasher.hash(password)
        except Exception as e:
            raise InvalidPasswordError(f"Password hashing failed: {str(e)}")

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify plain text password terhadap hash.

        Args:
            password: Plain text password
            password_hash: Hashed password dari database

        Returns:
            bool: True jika password match, False sebaliknya
        """
        try:
            self.hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False


class DokterRegistrationService:
    """
    Service untuk dokter registration logic.
    """

    def __init__(
        self,
        repository: DokterRepository,
        password_service: PasswordService
    ):
        """
        Initialize service dengan dependencies.
        Mengikuti Dependency Injection pattern.

        Args:
            repository: DokterRepository untuk database operations
            password_service: PasswordService untuk password operations
        """
        self.repository = repository
        self.password_service = password_service

    def register_dokter(self, request: DokterRegisterRequest) -> Dokter:
        """
        Mendaftarkan dokter baru dalam sistem.

        Args:
            request: DokterRegisterRequest dengan data dokter

        Returns:
            Dokter: Dokter yang telah terdaftar

        Raises:
            DuplicateEmailError: Jika email sudah terdaftar
            InvalidPasswordError: Jika password tidak valid
        """
        # Validasi email belum terdaftar
        if self.repository.exists_by_email(request.email):
            raise DuplicateEmailError(
                f"Email '{request.email}' sudah terdaftar dalam sistem"
            )

        # Hash password
        password_hash = self.password_service.hash_password(request.password)

        # Buat instance Dokter dengan data dari request
        dokter = Dokter(
            id=uuid4(),
            nama=request.nama,
            email=request.email,
            no_telepon=request.no_telepon,
            password_hash=password_hash,
            spesialisasi=request.spesialisasi,
            is_active=True,
        )

        # Simpan ke database
        saved_dokter = self.repository.create(dokter)
        return saved_dokter
