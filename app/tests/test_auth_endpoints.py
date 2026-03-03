"""
[TDD - RED PHASE] Integration tests untuk endpoint POST /api/v1/auth/login.
Menguji perilaku API end-to-end via HTTP.
"""

import pytest

BASE_URL = "/api/v1/auth/login"

VALID_PASSWORD  = "SecurePass123!"
WRONG_PASSWORD  = "WrongPass999!"
DOKTER_EMAIL    = "dokter@hospital.com"
ADMIN_EMAIL     = "admin@hospital.com"
PASIEN_EMAIL    = "pasien@hospital.com"
INACTIVE_EMAIL  = "inactive@hospital.com"


class TestLoginEndpoint:

    # Positive cases

    def test_login_dokter_returns_200_and_token(self, test_client, seeded_dokter):
        """Positive: Login dokter valid harus return 200 dengan access_token."""
        response = test_client.post(
            BASE_URL, json={"email": DOKTER_EMAIL, "password": VALID_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "DOKTER"

    def test_login_admin_returns_200_with_admin_role(self, test_client, seeded_admin):
        """Positive: Login admin valid harus return role ADMIN."""
        response = test_client.post(
            BASE_URL, json={"email": ADMIN_EMAIL, "password": VALID_PASSWORD}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "ADMIN"

    def test_login_pasien_returns_200_with_pasien_role(self, test_client, seeded_pasien):
        """Positive: Login pasien valid harus return role PASIEN."""
        response = test_client.post(
            BASE_URL, json={"email": PASIEN_EMAIL, "password": VALID_PASSWORD}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "PASIEN"

    # Security: OWASP A07

    def test_wrong_password_returns_401(self, test_client, seeded_dokter):
        """Negative [OWASP A07]: Password salah harus return 401 Unauthorized."""
        response = test_client.post(
            BASE_URL, json={"email": DOKTER_EMAIL, "password": WRONG_PASSWORD}
        )
        assert response.status_code == 401

    def test_nonexistent_email_returns_401(self, test_client):
        """Negative [OWASP A07]: Email tidak terdaftar harus return 401."""
        response = test_client.post(
            BASE_URL, json={"email": "tidakada@hospital.com", "password": VALID_PASSWORD}
        )
        assert response.status_code == 401

    def test_error_message_is_generic_for_wrong_password(self, test_client, seeded_dokter):
        """
        Security [OWASP A07]: Pesan error password salah harus generic.
        Tidak boleh menyebut 'password salah' secara eksplisit.
        """
        response = test_client.post(
            BASE_URL, json={"email": DOKTER_EMAIL, "password": WRONG_PASSWORD}
        )
        detail = response.json()["detail"].lower()
        assert "email atau password" in detail
        assert "password salah" not in detail
        assert "email tidak ditemukan" not in detail

    def test_error_message_identical_for_wrong_password_and_missing_email(
        self, test_client, seeded_dokter
    ):
        """
        Security [OWASP A07 — Anti User Enumeration]:
        Pesan error password salah == pesan error email tidak ada.
        """
        wrong_pw = test_client.post(
            BASE_URL, json={"email": DOKTER_EMAIL, "password": WRONG_PASSWORD}
        )
        missing_email = test_client.post(
            BASE_URL, json={"email": "tidakada@hospital.com", "password": VALID_PASSWORD}
        )
        assert wrong_pw.json()["detail"] == missing_email.json()["detail"]

    def test_inactive_dokter_returns_401(self, test_client, seeded_inactive_dokter):
        """Negative: Dokter tidak aktif harus ditolak login."""
        response = test_client.post(
            BASE_URL, json={"email": INACTIVE_EMAIL, "password": VALID_PASSWORD}
        )
        assert response.status_code == 401

    # Security: OWASP A02

    def test_response_must_not_expose_password_hash(self, test_client, seeded_dokter):
        """Security [OWASP A02]: Response tidak boleh mengandung password_hash."""
        response = test_client.post(
            BASE_URL, json={"email": DOKTER_EMAIL, "password": VALID_PASSWORD}
        )
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    # Validation (422)

    def test_missing_email_returns_422(self, test_client):
        """Negative: Request tanpa email harus return 422."""
        response = test_client.post(BASE_URL, json={"password": VALID_PASSWORD})
        assert response.status_code == 422

    def test_missing_password_returns_422(self, test_client):
        """Negative: Request tanpa password harus return 422."""
        response = test_client.post(BASE_URL, json={"email": DOKTER_EMAIL})
        assert response.status_code == 422

    def test_invalid_email_format_returns_422(self, test_client):
        """Negative: Format email tidak valid harus return 422."""
        response = test_client.post(
            BASE_URL, json={"email": "bukan-email", "password": VALID_PASSWORD}
        )
        assert response.status_code == 422

    def test_empty_body_returns_422(self, test_client):
        """Negative: Body kosong harus return 422."""
        response = test_client.post(BASE_URL, json={})
        assert response.status_code == 422
