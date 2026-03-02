from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.repositories.interfaces import IPasienRepository
from app.schemas.pasien_schema import UpdateProfilePayload
from app.domain.pasien import Pasien

password_hasher = PasswordHasher()

class NotFoundException(Exception):
    pass

def mask_phone_number(no_hp: str) -> str:
    if len(no_hp) > 6:
        return f"{no_hp[:4]}****{no_hp[-4:]}"
    return no_hp

def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(hashed_password, password)
    except VerifyMismatchError:
        return False

def get_profile(repo: IPasienRepository, pasien_id: str) -> Pasien:
    pasien = repo.get_by_id(pasien_id)
    if not pasien:
        raise NotFoundException(f"Pasien {pasien_id} not found")
    return pasien

def update_profile(repo: IPasienRepository, pasien_id: str, payload: UpdateProfilePayload) -> Pasien:
    pasien = repo.get_by_id(pasien_id)
    if not pasien:
        raise NotFoundException("Pasien not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return pasien

    if "password" in update_data:
        pasien.password_hash = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(pasien, key, value)

    return repo.update(pasien)