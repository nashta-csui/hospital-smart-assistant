import pytest
from pydantic import ValidationError
from app.schemas.pasien_schema import UpdateProfilePayload, ProfileResponse

def test_update_payload_positive_normalization():
    payload = UpdateProfilePayload(no_telepon="0812-3456 7890")
    assert payload.no_telepon == "081234567890"

def test_update_payload_positive_full_valid():
    payload = UpdateProfilePayload(
        nama="Budi Santoso",
        no_telepon="081234567890",
        alamat="Jl. Mangga Raya No. 10",
        golongan_darah="AB",
        password="secret123"
    )
    assert payload.nama == "Budi Santoso"
    assert payload.no_telepon == "081234567890"
    assert payload.golongan_darah == "AB"

def test_update_payload_positive_partial():
    payload = UpdateProfilePayload(alamat="Jl. Jeruk No. 5")
    dump = payload.model_dump(exclude_unset=True)
    assert dump == {"alamat": "Jl. Jeruk No. 5"}

def test_update_payload_positive_all_blood_types():
    for bt in ["A", "B", "AB", "O"]:
        payload = UpdateProfilePayload(golongan_darah=bt)
        assert payload.golongan_darah == bt

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

def test_update_payload_negative_name():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(nama="Ab")

def test_update_payload_negative_address():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(alamat="a")

def test_update_payload_negative_blood_type():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(golongan_darah="C")

def test_password_too_short():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(password="abc")

def test_password_no_digit():
    with pytest.raises(ValidationError):
        UpdateProfilePayload(password="passwordtanpaangka")

def test_update_payload_empty():
    with pytest.raises(ValidationError):
        UpdateProfilePayload()

def test_update_payload_read_only_injection():
    payload = UpdateProfilePayload(nama="Budi", id_pasien="123", nik="HACKED")
    dump = payload.model_dump(exclude_unset=True)
    assert "id_pasien" not in dump
    assert "nik" not in dump
    assert dump["nama"] == "Budi"

def test_profile_response_no_masking_in_schema():
    resp = ProfileResponse(
        id_pasien="1",
        nama="Budi",
        no_telepon="081234567890",
        alamat="Jl. Mangga",
        golongan_darah="A"
    )
    dump = resp.model_dump()
    assert dump["no_telepon"] == "081234567890"
