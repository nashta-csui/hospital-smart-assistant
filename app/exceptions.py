class InvalidCredentialsError(ApplicationException):
    """
    Raised ketika kredensial login tidak valid.
    SENGAJA dibuat generic (tidak menyebut 'password salah' atau 'email tidak ada')
    untuk mencegah User Enumeration Attack [OWASP A07].
    """
    pass


class InvalidTokenError(ApplicationException):
    """Raised ketika JWT token tidak valid atau sudah expired."""
    pass
