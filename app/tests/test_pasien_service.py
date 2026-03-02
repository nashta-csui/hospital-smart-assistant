import pytest
from pydantic import ValidationError
from app.domain.pasien import Pasien
from app.schemas.pasien_schema import UpdateProfilePayload
from app.repositories.in_memory_repository import InMemoryPasienRepository
from app.repositories.interfaces import IPasienRepository
from app.services.pasien_profile_service import (
    get_profile,
    update_profile,
    NotFoundException,
    mask_phone_number,
    hash_password,
    verify_password,
)

@pytest.fixture
def repo():
    r = InMemoryPasienRepository()
    p = Pasien(
        id_pasien="1",
        nomor_rekam_medis="RM-001",
        nik="1234567890",
        nama="Santi",
        no_telepon="081234567890",
        jenis_kelamin="P",
        tanggal_lahir="1990-01-01",
        alamat="Jl. Melati",
        email="Santi@email.com",
        golongan_darah="A",
        password_hash="hashed_pw"
    )
    r.data["1"] = p
    return r

# Positive Cases
def test_get_profile_success(repo):
    p = get_profile(repo, "1")
    assert p is not None
    assert p.nama == "Santi"

def test_update_profile_success(repo):
    payload = UpdateProfilePayload(alamat="Jl. Apel")
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Santi"
    assert updated.alamat == "Jl. Apel"

def test_update_profile_partial(repo):
    payload = UpdateProfilePayload(alamat="Jl. Anggrek")
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Santi"
    assert updated.alamat == "Jl. Anggrek"

def test_update_profile_password_hashed(repo):
    payload = UpdateProfilePayload(password="secret123")
    updated = update_profile(repo, "1", payload)

    assert updated.password_hash != "secret123"
    assert "secret123" not in updated.password_hash

def test_update_profile_password_only_does_not_change_other_fields(repo):
    payload = UpdateProfilePayload(password="newpass123")
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Santi"
    assert updated.alamat == "Jl. Melati"
    assert updated.no_telepon == "081234567890"
    assert updated.golongan_darah == "A"
    assert updated.password_hash != "hashed_pw"

def test_update_profile_all_fields(repo):
    payload = UpdateProfilePayload(
        no_telepon="089876543210",
        alamat="Jl. Apel",
        password="newpass123"
    )
    updated = update_profile(repo, "1", payload)

    assert updated.nama == "Santi"
    assert updated.no_telepon == "089876543210"
    assert updated.alamat == "Jl. Apel"
    assert updated.golongan_darah == "A"
    assert updated.password_hash != "newpass123"

def test_update_profile_same_value(repo):
    payload = UpdateProfilePayload(alamat="Jl. Melati")
    updated = update_profile(repo, "1", payload)
    assert updated.alamat == "Jl. Melati"

def test_update_then_get_profile(repo):
    payload = UpdateProfilePayload(alamat="Jl. Kenanga")
    update_profile(repo, "1", payload)
    
    result = get_profile(repo, "1")
    assert result.alamat == "Jl. Kenanga"

# Negative Cases
def test_get_profile_not_found(repo):
    with pytest.raises(NotFoundException):
        get_profile(repo, "999")

def test_update_profile_not_found(repo):
    payload = UpdateProfilePayload(alamat="Jl. Profile")
    with pytest.raises(NotFoundException):
        update_profile(repo, "999", payload)

def test_update_profile_reject_nama_field(repo):
    with pytest.raises(ValidationError):
        UpdateProfilePayload.model_validate({"nama": "Santi Baru", "alamat": "Jl. Apel"})

def test_update_profile_reject_golongan_darah_field(repo):
    with pytest.raises(ValidationError):
        UpdateProfilePayload.model_validate({"golongan_darah": "B", "alamat": "Jl. Apel"})

# Corner Cases
def test_mask_phone_number_short():
    assert mask_phone_number("12345") == "12345"

def test_hash_password_uses_argon2_and_can_verify():
    hashed = hash_password("abc12345")
    assert hashed.startswith("$argon2")
    assert hashed != "abc12345"
    assert verify_password("abc12345", hashed)
    assert not verify_password("wrongpass", hashed)

def test_update_profile_with_empty_payload_returns_same(repo):
    pasien_before = repo.get_by_id("1")

    class EmptyPayload:
        def model_dump(self, exclude_unset=True):
            return {}

    returned = update_profile(repo, "1", EmptyPayload())
    assert returned.id_pasien == pasien_before.id_pasien
    assert returned.nama == pasien_before.nama

def test_calling_abstract_methods_executes_pass_lines():
    res1 = IPasienRepository.get_by_id(None, "nope")
    assert res1 is None

    dummy = Pasien(
        id_pasien="x",
        nomor_rekam_medis="RM-0",
        nik="0",
        nama="x",
        no_telepon="0000000000",
        jenis_kelamin="P",
        tanggal_lahir="1990-01-01",
        alamat="x",
        email="x@x.com",
        golongan_darah="A",
        password_hash="h",
    )
    res2 = IPasienRepository.update(None, dummy)
    assert res2 is None