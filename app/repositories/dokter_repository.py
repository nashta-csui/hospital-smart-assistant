from abc import ABC, abstractmethod
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.base.dokter import Dokter
from app.exceptions import DuplicateEmailError, DatabaseError


class DokterRepository(ABC):
    """
    Abstract base class untuk Dokter repository.
    Mendefinisikan contract yang harus diimplementasi oleh concrete repository.
    Mengikuti Dependency Inversion Principle.
    """

    @abstractmethod
    def create(self, dokter: Dokter) -> Dokter:
        """
        Membuat dokter baru dalam database.

        Args:
            dokter: Instance Dokter yang akan disimpan

        Returns:
            Dokter: Dokter yang telah disimpan dengan ID

        Raises:
            DuplicateEmailError: Jika email sudah terdaftar
            DatabaseError: Jika ada error saat menyimpan ke database
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Dokter | None:
        """
        Mengambil dokter berdasarkan email.

        Args:
            email: Email dokter yang dicari

        Returns:
            Dokter | None: Dokter jika ditemukan, None sebaliknya

        Raises:
            DatabaseError: Jika ada error saat query database
        """
        pass

    @abstractmethod
    def get_by_id(self, dokter_id: UUID) -> Dokter | None:
        """
        Mengambil dokter berdasarkan ID.

        Args:
            dokter_id: UUID dokter yang dicari

        Returns:
            Dokter | None: Dokter jika ditemukan, None sebaliknya

        Raises:
            DatabaseError: Jika ada error saat query database
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Mengecek apakah email sudah terdaftar.

        Args:
            email: Email yang dicek

        Returns:
            bool: True jika email sudah ada, False sebaliknya
        """
        pass


class SQLAlchemyDokterRepository(DokterRepository):
    """
    Implementasi konkret DokterRepository menggunakan SQLAlchemy.
    Menangani semua operasi database untuk Dokter entity.
    """

    def __init__(self, session: Session):
        """
        Initialize repository dengan SQLAlchemy session.

        Args:
            session: SQLAlchemy Session untuk database operations
        """
        self.session = session

    def create(self, dokter: Dokter) -> Dokter:
        """Membuat dokter baru dalam database."""
        try:
            self.session.add(dokter)
            self.session.commit()
            self.session.refresh(dokter)
            return dokter
        except IntegrityError as e:
            self.session.rollback()
            # Check if it's a duplicate email error
            if "email" in str(e).lower():
                raise DuplicateEmailError(f"Email '{dokter.email}' sudah terdaftar")
            raise DatabaseError(f"Integrity constraint violation: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Database error saat membuat dokter: {str(e)}")

    def get_by_email(self, email: str) -> Dokter | None:
        """Mengambil dokter berdasarkan email."""
        try:
            return self.session.query(Dokter).filter(
                Dokter.email == email
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error saat query email: {str(e)}")

    def get_by_id(self, dokter_id: UUID) -> Dokter | None:
        """Mengambil dokter berdasarkan ID."""
        try:
            return self.session.query(Dokter).filter(
                Dokter.id == dokter_id
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error saat query ID: {str(e)}")

    def exists_by_email(self, email: str) -> bool:
        """Mengecek apakah email sudah terdaftar."""
        try:
            return self.session.query(Dokter).filter(
                Dokter.email == email
            ).first() is not None
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error saat check email: {str(e)}")
