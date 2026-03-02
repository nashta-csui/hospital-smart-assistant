"""
Custom exceptions untuk application layer.
Mengikuti SOLID principles dengan specific exception types untuk better error handling.
"""


class ApplicationException(Exception):
    """Base exception untuk semua application errors."""
    pass


class DuplicateEmailError(ApplicationException):
    """Raised ketika email sudah terdaftar dalam sistem."""
    pass


class DuplicatePhoneError(ApplicationException):
    """Raised ketika nomor telepon sudah terdaftar dalam sistem."""
    pass


class InvalidPasswordError(ApplicationException):
    """Raised ketika password tidak memenuhi kriteria keamanan."""
    pass


class DokterNotFoundError(ApplicationException):
    """Raised ketika dokter tidak ditemukan dalam database."""
    pass


class RepositoryError(ApplicationException):
    """Base exception untuk repository layer errors."""
    pass


class DatabaseError(RepositoryError):
    """Raised ketika ada error dalam database operation."""
    pass
