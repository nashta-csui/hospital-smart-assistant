import pytest
from fastapi import HTTPException
from unittest.mock import Mock

from app.main import register_dokter, get_password_service, get_db
from app.exceptions import InvalidPasswordError, DatabaseError
from app.schemas.dokter import DokterRegisterRequest


def test_get_password_service_returns_instance():
    service = get_password_service()
    assert service is not None


def test_get_db_yields_session():
    gen = get_db()
    db = next(gen)
    assert db is not None
    gen.close()

def test_register_dokter_invalid_password(test_client, monkeypatch):
    from app.services.dokter_service import DokterRegistrationService

    def fake_register(*args, **kwargs):
        raise InvalidPasswordError("invalid")

    monkeypatch.setattr(
        DokterRegistrationService,
        "register_dokter",
        fake_register
    )

    payload = {
        "nama": "Dr. Test",
        "email": "test@test.com",
        "no_telepon": "081234567890",
        "password": "SecurePass123!",
        "spesialisasi": "Test"
    }

    response = test_client.post("/dokter/register", json=payload)
    assert response.status_code == 400

def test_register_dokter_database_error(test_client, monkeypatch):
    from app.services.dokter_service import DokterRegistrationService

    def fake_register(*args, **kwargs):
        raise DatabaseError("db error")

    monkeypatch.setattr(
        DokterRegistrationService,
        "register_dokter",
        fake_register
    )

    payload = {
        "nama": "Dr. Test",
        "email": "test2@test.com",
        "no_telepon": "081234567890",
        "password": "SecurePass123!",
        "spesialisasi": "Test"
    }

    response = test_client.post("/dokter/register", json=payload)
    assert response.status_code == 500

def test_register_dokter_unexpected_exception(test_client, monkeypatch):
    from app.services.dokter_service import DokterRegistrationService

    def fake_register(*args, **kwargs):
        raise Exception("unknown")

    monkeypatch.setattr(
        DokterRegistrationService,
        "register_dokter",
        fake_register
    )

    payload = {
        "nama": "Dr. Test",
        "email": "test3@test.com",
        "no_telepon": "081234567890",
        "password": "SecurePass123!",
        "spesialisasi": "Test"
    }

    response = test_client.post("/dokter/register", json=payload)
    assert response.status_code == 500

def test_get_dokter_registration_service(test_db):
    from app.main import get_dokter_registration_service
    from app.services.dokter_service import DokterRegistrationService

    service = get_dokter_registration_service(test_db)
    assert isinstance(service, DokterRegistrationService)