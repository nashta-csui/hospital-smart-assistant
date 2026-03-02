from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base.base_model import Base, Email


class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    email: Mapped[Email] = mapped_column(unique=True)
    """Email yang digunakan oleh admin untuk login; unique"""

    password_hash: Mapped[str]
    """Password admin yang di-hash menggunakan Argon2"""

    nama: Mapped[str] = mapped_column(String(255))
    """Nama lengkap admin"""
