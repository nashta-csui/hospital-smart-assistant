"""
Integration tests untuk endpoint HTTP Dokter.
Seluruh perilaku API diuji end-to-end menggunakan TestClient.
"""

import pytest

# Admin token untuk testing
ADMIN_TOKEN = "test-admin-token-12345"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


class TestDokterRegistrationEndpoint:
    """Tes register doctor via HTTP."""

    def test_successful_registration(self, test_client):
        payload = {
            "nama": "Dr. Budi Santoso",
            "email": "budi@hospital.com",
            "no_telepon": "081234567890",
            "password": "SecurePass123!",
            "spesialisasi": "Kardiologi"
        }

        response = test_client.post("/dokter/register", json=payload, headers=ADMIN_HEADERS)
        assert response.status_code == 201
        data = response.json()
        assert data["nama"] == payload["nama"]
        assert data["email"] == payload["email"]
        assert data["spesialisasi"] == payload["spesialisasi"]
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_registration_without_authorization_returns_401(self, test_client):
        payload = {
            "nama": "Dr. Budi Santoso",
            "email": "budi@hospital.com",
            "no_telepon": "081234567890",
            "password": "SecurePass123!",
            "spesialisasi": "Kardiologi"
        }

        # Request tanpa authorization header
        response = test_client.post("/dokter/register", json=payload)
        assert response.status_code == 401
        assert "Authorization header" in response.json()["detail"]

    def test_registration_with_invalid_authorization_returns_401(self, test_client):
        payload = {
            "nama": "Dr. Budi Santoso",
            "email": "budi@hospital.com",
            "no_telepon": "081234567890",
            "password": "SecurePass123!",
            "spesialisasi": "Kardiologi"
        }

        # Request dengan invalid authorization header
        response = test_client.post(
            "/dokter/register",
            json=payload,
            headers={"Authorization": "InvalidFormat"}
        )
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

    def test_duplicate_email_returns_400(self, test_client):
        payload = {
            "nama": "Dr. Budi Santoso",
            "email": "budi@hospital.com",
            "no_telepon": "081234567890",
            "password": "SecurePass123!",
            "spesialisasi": "Kardiologi"
        }
        r1 = test_client.post("/dokter/register", json=payload, headers=ADMIN_HEADERS)
        assert r1.status_code == 201

        # try again with same email
        payload2 = payload.copy()
        payload2["nama"] = "Dr. Budi II"
        r2 = test_client.post("/dokter/register", json=payload2, headers=ADMIN_HEADERS)
        assert r2.status_code == 400
        assert "email" in r2.json()["detail"].lower()

    @pytest.mark.parametrize("bad_payload", [
        {"nama": "Dr", "email": "budi@hospital.com", "no_telepon": "081234567890", "password": "SecurePass123!", "spesialisasi": "Kardiologi"},
        {"nama": "Dr. Budi", "email": "not-an-email", "no_telepon": "081234567890", "password": "SecurePass123!", "spesialisasi": "Kardiologi"},
        {"nama": "Dr. Budi", "email": "budi@hospital.com", "no_telepon": "123", "password": "SecurePass123!", "spesialisasi": "Kardiologi"},
        {"nama": "Dr. Budi", "email": "budi@hospital.com", "no_telepon": "081234567890", "password": "short", "spesialisasi": "Kardiologi"},
        {"nama": "Dr. Budi", "email": "budi@hospital.com", "no_telepon": "081234567890", "password": "SecurePass123!"}  # missing spesialisasi
    ])
    def test_validation_errors_return_422(self, test_client, bad_payload):
        response = test_client.post("/dokter/register", json=bad_payload, headers=ADMIN_HEADERS)
        assert response.status_code == 422
