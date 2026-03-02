from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class UpdateProfilePayload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    no_telepon: Optional[str] = None
    alamat: Optional[str] = Field(None, min_length=3)
    password: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def reject_immutable_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            forbidden_fields = {"nama", "golongan_darah"}
            sent_forbidden = sorted(forbidden_fields.intersection(data.keys()))
            if sent_forbidden:
                raise ValueError(f"Fields cannot be updated: {', '.join(sent_forbidden)}")
        return data

    @field_validator("no_telepon", mode="before")
    @classmethod
    def sanitize_phone(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.replace(" ", "").replace("-", "")
            if not v:
                raise ValueError("Phone cannot be empty")
            if not v.isdigit():
                raise ValueError("Phone must contain only numbers")
            if len(v) < 10 or len(v) > 15:
                raise ValueError("Phone length must be between 10 and 15 digits")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 8:
                raise ValueError("Password must be at least 8 characters long")
            if not any(c.isdigit() for c in v):
                raise ValueError("Password must contain at least one digit")
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UpdateProfilePayload":
        if not self.model_dump(exclude_unset=True):
            raise ValueError("Update payload cannot be empty. Must provide at least one field to update.")
        return self

class ProfileResponse(BaseModel):
    id_pasien: str
    nomor_rekam_medis: str
    nama: str
    no_telepon: str
    jenis_kelamin: str
    tanggal_lahir: date
    alamat: str
    email: str
    golongan_darah: str