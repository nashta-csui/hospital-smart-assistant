import pytest
from pydantic import ValidationError
from app.schemas.pasien_schema import UpdateProfilePayload, ProfileResponse

# Positive Cases
def test_update_payload_positive_normalization():
    payload = UpdateProfilePayload(no_telepon="0812-3456 7890")
    assert payload.no_telepon == "081234567890"

def test_update_payload_positive_full_valid():
    payload = UpdateProfilePayload(
        no_telepon="081234567890",
        alamat="Jl. Melati Raya No. 10",
        password="secret123"
    )
    assert payload.no_telepon == "081234567890"

def test_update_payload_positive_partial():
    payload = UpdateProfilePayload(alamat="Jl. Anggrek No. 5")
    dump = payload.model_dump(exclude_unset=True)
    assert dump == {"alamat": "Jl. Anggrek No. 5"}

# Negative Cases
def test_update_payload_golongan_darah_forbidden():
    with pytest.raises(ValidationError):
        UpdateProfilePayload.model_validate({"golongan_darah": "AB", "alamat": "Jl. Cemara"})

def test_phone_too_short():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(no_telepon="0812")

def test_phone_too_long():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(no_telepon="081234567890123456")

def test_phone_contains_letters():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(no_telepon="08AB123456")

def test_phone_only_spaces():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(no_telepon="   ")

def test_update_payload_nama_forbidden():
    with pytest.raises(ValidationError):
        UpdateProfilePayload.model_validate({"nama": "Abc", "alamat": "Jl. Mawar"})

def test_update_payload_negative_address():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(alamat="a")

def test_update_payload_invalid_golongan_darah_forbidden():
    with pytest.raises(ValidationError):
        UpdateProfilePayload.model_validate({"golongan_darah": "C", "alamat": "Jl. Nusa"})

def test_password_too_short():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(password="abc")

def test_password_no_digit():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(password="passwordtanpaangka")

# Corner Cases
def test_update_payload_empty():
    with pytest.raises(ValidationError):
        UpdateProfilePayload()

def test_update_payload_read_only_injection():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(nama="Santi", id_pasien="123", nik="HACKED")

def test_profile_response_no_masking_in_schema():
    resp = ProfileResponse(
        id_pasien="1",
        nomor_rekam_medis="RM-001",
        nama="Santi",
        no_telepon="081234567890",
        jenis_kelamin="P",
        tanggal_lahir="1990-01-01",
        alamat="Jl. Melati",
        email="Santi@email.com",
        golongan_darah="A"
    )
    dump = resp.model_dump()
    assert dump["no_telepon"] == "081234567890"
