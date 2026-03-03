"""
[TDD - RED PHASE] Unit tests untuk fitur Authentication Login.

Covers:
- Schema validation (LoginRequest)
- Repository layer (AuthRepository)
- Token service (TokenService / JWT)
- Service layer (AuthService / business logic)
"""

import pytest
import datetime
from uuid import uuid4
from unittest.mock import patch

from app.schemas.auth import LoginRequest, LoginResponse
from app.repositories.auth_repository import AuthRepository, SQLAlchemyAuthRepository
from app.services.auth_service import AuthService, TokenService
from app.exceptions import InvalidCredentialsError, InvalidTokenError, DatabaseError
from app.models.base.dokter import Dokter
from app.models.base.admin import Admin
from app.models.base.pasien import Pasien

# Konstanta (sama dengan conftest)
VALID_PASSWORD  = "SecurePass123!"
WRONG_PASSWORD  = "WrongPass999!"
DOKTER_EMAIL    = "dokter@hospital.com"
ADMIN_EMAIL     = "admin@hospital.com"
PASIEN_EMAIL    = "pasien@hospital.com"
INACTIVE_EMAIL  = "inactive@hospital.com"

# 1. SCHEMA VALIDATION
class TestLoginRequest:
    """Validasi input schema LoginRequest."""

    def test_valid_login_request_should_pass_validation(self):
        """Positive: Data valid harus lolos validasi tanpa error."""
        request = LoginRequest(
            email="user@hospital.com",
            password="SecurePass123!"
        )
        assert request.email == "user@hospital.com"
        assert request.password == "SecurePass123!"

    def test_invalid_email_format_should_fail(self):
        """Negative: Format email tidak valid harus raise ValidationError."""
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            LoginRequest(email="bukan-email", password="SecurePass123!")

    def test_empty_password_should_fail(self):
        """Negative: Password kosong harus ditolak."""
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            LoginRequest(email="user@hospital.com", password="")

    def test_missing_email_should_fail(self):
        """Negative: Request tanpa email harus ditolak."""
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            LoginRequest(password="SecurePass123!")

    def test_missing_password_should_fail(self):
        """Negative: Request tanpa password harus ditolak."""
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            LoginRequest(email="user@hospital.com")

# 2. REPOSITORY LAYER
class TestAuthRepository:
    """
    Test AuthRepository: find_user_by_email harus cari ke 3 tabel
    dan return (user_object, role_string) atau None.
    """

    def test_find_dokter_by_email_should_return_dokter_with_role(
        self,
        auth_repository: SQLAlchemyAuthRepository,
        seeded_dokter: Dokter
    ):
        """Positive: Email dokter harus return tuple (Dokter, 'DOKTER')."""
        result = auth_repository.find_user_by_email(DOKTER_EMAIL)

        assert result is not None
        user, role = result
        assert role == "DOKTER"
        assert isinstance(user, Dokter)
        assert user.email == DOKTER_EMAIL

    def test_find_admin_by_email_should_return_admin_with_role(
        self,
        auth_repository: SQLAlchemyAuthRepository,
        seeded_admin: Admin
    ):
        """Positive: Email admin harus return tuple (Admin, 'ADMIN')."""
        result = auth_repository.find_user_by_email(ADMIN_EMAIL)

        assert result is not None
        user, role = result
        assert role == "ADMIN"
        assert isinstance(user, Admin)

    def test_find_pasien_by_email_should_return_pasien_with_role(
        self,
        auth_repository: SQLAlchemyAuthRepository,
        seeded_pasien: Pasien
    ):
        """Positive: Email pasien harus return tuple (Pasien, 'PASIEN')."""
        result = auth_repository.find_user_by_email(PASIEN_EMAIL)

        assert result is not None
        user, role = result
        assert role == "PASIEN"
        assert isinstance(user, Pasien)

    def test_email_not_in_any_table_should_return_none(
        self,
        auth_repository: SQLAlchemyAuthRepository
    ):
        """Negative: Email yang tidak ada di semua tabel harus return None."""
        result = auth_repository.find_user_by_email("tidakada@hospital.com")
        assert result is None

    def test_find_user_should_raise_database_error_on_query_failure(
        self,
        auth_repository: SQLAlchemyAuthRepository
    ):
        """Negative: Query gagal harus raise DatabaseError, bukan SQLAlchemyError mentah."""
        from sqlalchemy.exc import SQLAlchemyError
        with patch.object(
            auth_repository.session, "query",
            side_effect=SQLAlchemyError("koneksi gagal")
        ):
            with pytest.raises(DatabaseError):
                auth_repository.find_user_by_email("test@test.com")


# 3. TOKEN SERVICE (JWT)
class TestTokenService:
    """Test TokenService: pembuatan dan validasi JWT."""

    def test_create_access_token_should_return_nonempty_string(self):
        """Positive: Token yang dibuat harus berupa string non-kosong."""
        service = TokenService()
        token = service.create_access_token(
            user_id=uuid4(), role="DOKTER", email="dokter@hospital.com"
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_payload_should_contain_correct_role(self):
        """Positive: Payload token harus mengandung role yang benar."""
        service = TokenService()
        token = service.create_access_token(uuid4(), "ADMIN", "admin@hospital.com")
        payload = service.decode_token(token)
        assert payload["role"] == "ADMIN"

    def test_token_payload_should_contain_user_id_as_sub(self):
        """Positive: Field 'sub' di payload harus berisi UUID user."""
        service = TokenService()
        user_id = uuid4()
        token = service.create_access_token(user_id, "PASIEN", "pasien@hospital.com")
        payload = service.decode_token(token)
        assert payload["sub"] == str(user_id)

    def test_token_should_have_expiration_field(self):
        """Positive [OWASP A02]: Token harus punya expiration time (exp)."""
        service = TokenService()
        token = service.create_access_token(uuid4(), "DOKTER", "dokter@hospital.com")
        payload = service.decode_token(token)
        assert "exp" in payload

    def test_decode_invalid_token_should_raise_invalid_token_error(self):
        """Negative: Token tidak valid / rusak harus raise InvalidTokenError."""
        service = TokenService()
        with pytest.raises(InvalidTokenError):
            service.decode_token("ini.bukan.token.valid.sama.sekali")

# 4. AUTH SERVICE (Business Logic)
class TestAuthService:
    """
    Test AuthService: orchestrasi login dari cari user,
    verifikasi password, cek status, hingga generate token.
    """

    def test_login_dokter_valid_credentials_should_return_response(
        self, auth_service: AuthService, seeded_dokter: Dokter
    ):
        """Positive: Dokter aktif dengan kredensial benar harus dapat token."""
        request = LoginRequest(email=DOKTER_EMAIL, password=VALID_PASSWORD)
        response = auth_service.login(request)

        assert response is not None
        assert response.access_token is not None
        assert response.token_type == "bearer"
        assert response.role == "DOKTER"

    def test_login_admin_valid_credentials_should_return_response(
        self, auth_service: AuthService, seeded_admin: Admin
    ):
        """Positive: Admin dengan kredensial benar harus dapat token dengan role ADMIN."""
        request = LoginRequest(email=ADMIN_EMAIL, password=VALID_PASSWORD)
        response = auth_service.login(request)

        assert response.role == "ADMIN"
        assert response.access_token is not None

    def test_login_pasien_valid_credentials_should_return_response(
        self, auth_service: AuthService, seeded_pasien: Pasien
    ):
        """Positive: Pasien dengan kredensial benar harus dapat token dengan role PASIEN."""
        request = LoginRequest(email=PASIEN_EMAIL, password=VALID_PASSWORD)
        response = auth_service.login(request)

        assert response.role == "PASIEN"
        assert response.access_token is not None

    def test_login_wrong_password_should_raise_invalid_credentials(
        self, auth_service: AuthService, seeded_dokter: Dokter
    ):
        """
        Negative [OWASP A07]: Password salah harus raise InvalidCredentialsError
        dengan pesan GENERIC — tidak menyebut 'password salah'.
        """
        request = LoginRequest(email=DOKTER_EMAIL, password=WRONG_PASSWORD)

        with pytest.raises(InvalidCredentialsError) as exc_info:
            auth_service.login(request)

        # Pesan harus generic
        error_msg = str(exc_info.value).lower()
        assert "email atau password" in error_msg

    def test_login_nonexistent_email_should_raise_same_error_as_wrong_password(
        self, auth_service: AuthService
    ):
        """
        Negative [OWASP A07 — User Enumeration Prevention]:
        Error untuk email tidak ada HARUS IDENTIK dengan error password salah.
        Jika beda, attacker bisa enumerate email yang terdaftar.
        """
        request = LoginRequest(email="tidakada@hospital.com", password=VALID_PASSWORD)

        with pytest.raises(InvalidCredentialsError) as exc_info:
            auth_service.login(request)

        error_msg = str(exc_info.value).lower()
        assert "email atau password" in error_msg

    def test_login_inactive_dokter_should_raise_invalid_credentials(
        self, auth_service: AuthService, seeded_inactive_dokter: Dokter
    ):
        """
        Negative: Dokter is_active=False tidak boleh login.
        Error message tetap GENERIC (tidak bilang 'akun nonaktif').
        """
        request = LoginRequest(email=INACTIVE_EMAIL, password=VALID_PASSWORD)

        with pytest.raises(InvalidCredentialsError):
            auth_service.login(request)

    def test_login_token_payload_should_contain_correct_role_and_id(
        self, auth_service: AuthService, seeded_dokter: Dokter
    ):
        """Positive: JWT yang dihasilkan harus embed role dan user_id yang benar."""
        request = LoginRequest(email=DOKTER_EMAIL, password=VALID_PASSWORD)
        response = auth_service.login(request)

        token_service = TokenService()
        payload = token_service.decode_token(response.access_token)

        assert payload["role"] == "DOKTER"
        assert payload["sub"] == str(seeded_dokter.id)
