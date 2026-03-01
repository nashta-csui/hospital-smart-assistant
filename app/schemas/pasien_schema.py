from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class UpdateProfilePayload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nama: Optional[str] = Field(None, min_length=3, max_length=100)
    no_telepon: Optional[str] = None
    alamat: Optional[str] = Field(None, min_length=3)
    golongan_darah: Optional[Literal["A", "B", "AB", "O"]] = None
    password: Optional[str] = None

    @field_validator("no_telepon", mode="before")
    @classmethod
    def sanitize_phone(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.replace(" ", "").replace("-", "")
            if not v:
                raise ValueError()
            if not v.isdigit():
                raise ValueError()
            if len(v) < 10 or len(v) > 15:
                raise ValueError()
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 8:
                raise ValueError()
            if not any(c.isdigit() for c in v):
                raise ValueError()
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UpdateProfilePayload":
        if not self.model_dump(exclude_unset=True):
            raise ValueError()
        return self

class ProfileResponse(BaseModel):
    id_pasien: str
    nama: str
    no_telepon: str
    alamat: str
    golongan_darah: str