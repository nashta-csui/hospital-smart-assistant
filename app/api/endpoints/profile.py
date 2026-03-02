from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.pasien_schema import ProfileResponse, UpdateProfilePayload
from app.api.deps import get_repo, get_current_user_id
from app.repositories.interfaces import IPasienRepository
from app.services.pasien_profile_service import get_profile, update_profile, mask_phone_number, NotFoundException

router = APIRouter()

@router.get(
    "/profile",
    response_model=ProfileResponse,
    responses={404: {"description": "Profile not found"}},
)
def get_profile_endpoint(
    user_id: Annotated[str, Depends(get_current_user_id)],
    repo: Annotated[IPasienRepository, Depends(get_repo)],
):
    try:
        pasien = get_profile(repo, user_id)
        data = pasien.model_dump()
        data["no_telepon"] = mask_phone_number(data["no_telepon"])
        return ProfileResponse(**data)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Profile not found")


@router.put(
    "/profile",
    response_model=ProfileResponse,
    responses={404: {"description": "Profile not found"}},
)
def update_profile_endpoint(
    payload: UpdateProfilePayload,
    user_id: Annotated[str, Depends(get_current_user_id)],
    repo: Annotated[IPasienRepository, Depends(get_repo)],
):
    try:
        updated_pasien = update_profile(repo, user_id, payload)
        data = updated_pasien.model_dump()
        data["no_telepon"] = mask_phone_number(data["no_telepon"])
        return ProfileResponse(**data)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Profile not found")