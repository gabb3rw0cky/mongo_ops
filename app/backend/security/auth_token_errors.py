class AuthTokenError(Exception):
    """Base exception for all authentication token errors."""

class TokenInputError(AuthTokenError):
    """Raised when input parameters are invalid or missing."""

class InvalidTokenError(AuthTokenError):
    """Raised when a token is expired, invalid, or cannot be parsed."""
