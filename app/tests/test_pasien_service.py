import pytest
from app.domain.pasien import Pasien
from app.schemas.pasien_schema import UpdateProfilePayload
from app.repositories.in_memory_repository import InMemoryPasienRepository
from app.services.pasien_profile_service import get_profile, update_profile, NotFoundException

@pytest.fixture
def repo():
    r = InMemoryPasienRepository()
    p = Pasien(
        id_pasien="1",
        nik="1234567890",
        nama="Budi",
        no_telepon="081234567890",
        alamat="Jl. Mangga",
        golongan_darah="A",
        password_hash="hashed_pw"
    )
    r.data["1"] = p
    return r

def test_get_profile_success(repo):
    p = get_profile(repo, "1")
    assert p is not None
    assert p.nama == "Budi"

def test_get_profile_not_found(repo):
    with pytest.raises(NotFoundException):
        get_profile(repo, "999")

def test_update_profile_success(repo):
    payload = UpdateProfilePayload(nama="Budi Baru", alamat="Jl. Apel")
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Budi Baru"
    assert updated.alamat == "Jl. Apel"

def test_update_profile_partial(repo):
    payload = UpdateProfilePayload(alamat="Jl. Jeruk")
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Budi"
    assert updated.alamat == "Jl. Jeruk"

def test_update_profile_not_found(repo):
    payload = UpdateProfilePayload(nama="Profile")
    with pytest.raises(NotFoundException):
        update_profile(repo, "999", payload)

def test_update_profile_password_hashed(repo):
    payload = UpdateProfilePayload(password="secret123")
    updated = update_profile(repo, "1", payload)

    assert updated.password_hash != "secret123"
    assert "secret123" not in updated.password_hash

def test_update_profile_password_only_does_not_change_other_fields(repo):
    payload = UpdateProfilePayload(password="newpass123")
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Budi"
    assert updated.alamat == "Jl. Mangga"
    assert updated.no_telepon == "081234567890"
    assert updated.golongan_darah == "A"
    assert updated.password_hash != "hashed_pw"

def test_update_profile_all_fields(repo):
    payload = UpdateProfilePayload(
        nama="Budi Baru",
        no_telepon="089876543210",
        alamat="Jl. Apel",
        golongan_darah="B",
        password="newpass123"
    )
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Budi Baru"
    assert updated.no_telepon == "089876543210"
    assert updated.alamat == "Jl. Apel"
    assert updated.golongan_darah == "B"
    assert updated.password_hash != "newpass123"

def test_update_profile_same_value(repo):
    payload = UpdateProfilePayload(nama="Budi")
    updated = update_profile(repo, "1", payload)
    assert updated.nama == "Budi"

def test_update_then_get_profile(repo):
    payload = UpdateProfilePayload(nama="Budi Baru")
    update_profile(repo, "1", payload)
    
    result = get_profile(repo, "1")
    assert result.nama == "Budi Baru"