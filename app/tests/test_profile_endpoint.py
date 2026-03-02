import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_repo
from app.repositories.in_memory_repository import InMemoryPasienRepository
from app.domain.pasien import Pasien

client = TestClient(app)

@pytest.fixture
def setup_repo():
    repo = InMemoryPasienRepository()
    p = Pasien(
        id_pasien="123",
        nik="1234567890",
        nama="Budi",
        no_telepon="081234567890",
        alamat="Jl. Mangga",
        golongan_darah="A",
        password_hash="hashed_pw"
    )
    repo.data["123"] = p
    app.dependency_overrides[get_repo] = lambda: repo
    yield repo
    app.dependency_overrides.clear()

def test_get_profile_endpoint_success(setup_repo):
    response = client.get("/api/v1/profile", headers={"Authorization": "Bearer user-123"})
    assert response.status_code == 200
    data = response.json()
    assert data["nama"] == "Budi"
    assert data["no_telepon"] == "0812****7890"

def test_get_profile_endpoint_not_found(setup_repo):
    response = client.get("/api/v1/profile", headers={"Authorization": "Bearer user-999"})
    assert response.status_code == 404

def test_update_profile_endpoint_success(setup_repo):
    response = client.put(
        "/api/v1/profile",
        json={"nama": "Budi Edit", "alamat": "Jl. Apel"},
        headers={"Authorization": "Bearer user-123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nama"] == "Budi Edit"
    assert data["alamat"] == "Jl. Apel"

def test_update_profile_endpoint_validation_error(setup_repo):
    response = client.put(
        "/api/v1/profile",
        json={"nama": "A"},
        headers={"Authorization": "Bearer user-123"}
    )
    assert response.status_code == 422

def test_update_profile_endpoint_not_found(setup_repo):
    response = client.put(
        "/api/v1/profile",
        json={"nama": "Budi Not Found"},
        headers={"Authorization": "Bearer user-999"}
    )
    assert response.status_code == 404

def test_update_profile_endpoint_empty_body(setup_repo):
    response = client.put(
        "/api/v1/profile",
        json={},
        headers={"Authorization": "Bearer user-123"}
    )
    assert response.status_code == 422

def test_update_profile_endpoint_no_body(setup_repo):
    response = client.put(
        "/api/v1/profile",
        headers={"Authorization": "Bearer user-123"}
    )
    assert response.status_code == 422

def test_auth_unauthorized():
    response = client.get("/api/v1/profile")
    assert response.status_code == 401

def test_auth_invalid_token_format():
    response = client.get("/api/v1/profile", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401

def test_auth_empty_token():
    response = client.get("/api/v1/profile", headers={"Authorization": "Bearer "})
    assert response.status_code == 401