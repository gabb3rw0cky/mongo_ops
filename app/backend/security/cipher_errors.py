class   CipherError(Exception):
    """Base exception for cipher-related failures."""

class   EncryptionError(CipherError):
    """Raised when encryption failures occur."""

class   InvalidEncryptedData(CipherError):
    """Raised when encrypted input is malformed or invalid."""

class   DecryptionError(CipherError):
    """Raised when decryption fails."""

class   InvalidEncryptionKey(CipherError):
    """Raised when the encryption key is invalid."""

class   EVP_BytesToKeyError(CipherError):
    """Raised when evp_bytes to key convertion fails."""

