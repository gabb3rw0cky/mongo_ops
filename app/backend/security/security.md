
# `README.md`

```markdown
# Security Encryption Utility

A Python utility for encrypting and decrypting JSON payloads using a format compatible with:

- **CryptoJS AES**
- **OpenSSL salted format**
- **AES-256-CBC**
- **EVP_BytesToKey (MD5)**

> This project is mainly intended for **legacy interoperability** with systems that already use CryptoJS/OpenSSL-style password-based encryption.

---

## Features

- Encrypt Python dictionaries to base64 strings
- Decrypt base64 strings back into Python dictionaries
- Compatible with payloads using the OpenSSL `Salted__` header
- Uses AES-256-CBC with PKCS#7 padding
- Strict input validation and custom exceptions

---

## Security Note

This library uses **OpenSSL EVP_BytesToKey with MD5**, which is a **legacy key derivation method**.

It is provided for compatibility with existing systems such as older CryptoJS/OpenSSL workflows.

### Recommended for new systems
For new applications, prefer:
- **AES-GCM** or **ChaCha20-Poly1305**
- **PBKDF2**, **scrypt**, or **Argon2** for password-based key derivation

This project does **not** currently provide authenticated encryption, so ciphertext tampering may only be detected indirectly during padding/JSON validation.

---

## Installation

Install dependencies:

```bash
pip install pycryptodome
```

---

## Project Structure

```text
Security/
├── __init__.py
├── Encryption.py
└── EncryptionError.py
```

---

## Quick Start

```python
from Security import Encryption

crypto = Encryption("my-secret-password")

encrypted = crypto.encrypt_payload({
    "user_id": 123,
    "role": "admin"
})

print("Encrypted:", encrypted)

decrypted = crypto.decrypt_payload(encrypted)
print("Decrypted:", decrypted)
```

---

## API Overview

### `Encryption`

Main class for encrypting and decrypting JSON payloads.

#### Constructor

```python
Encryption(key: str)
```

Creates a new encryption helper using the provided password string.

**Parameters**
- `key` (`str`): Non-empty password used to derive the AES key and IV

**Raises**
- `InvalidEncryptionKey`: If the key is empty or not a string

---

### `encrypt_payload`

```python
encrypt_payload(data: Mapping[str, Any]) -> str
```

Encrypts a dictionary-like object and returns a base64-encoded encrypted string.

**Parameters**
- `data`: A JSON-serializable dictionary or mapping

**Returns**
- `str`: Base64-encoded encrypted payload

**Raises**
- `EncryptionError`: If serialization or encryption fails

**Example**
```python
crypto = Encryption("secret")
token = crypto.encrypt_payload({"name": "Alice", "active": True})
```

---

### `decrypt_payload`

```python
decrypt_payload(encrypted: str) -> dict
```

Decrypts a base64-encoded encrypted string and returns the original dictionary.

**Parameters**
- `encrypted` (`str`): Base64-encoded encrypted payload

**Returns**
- `dict`: Decrypted JSON object

**Raises**
- `InvalidEncryptedData`: If the payload is malformed, invalid, or cannot be decrypted
- `DecryptionError`: If an unexpected decryption error occurs

**Example**
```python
crypto = Encryption("secret")
data = crypto.decrypt_payload(token)
```

---

## Encrypted Payload Format

The encrypted output uses this binary layout before base64 encoding:

```text
b"Salted__" + salt(8 bytes) + ciphertext
```

Where:
- `Salted__` is the OpenSSL header
- `salt` is 8 random bytes
- `ciphertext` is AES-CBC-encrypted JSON with PKCS#7 padding

---

## Compatibility

This module is intended to be compatible with CryptoJS/OpenSSL-style encryption that uses:

- password-based AES-CBC
- OpenSSL salted payload framing
- EVP_BytesToKey with MD5

If your external system uses a different KDF, mode, or payload format, compatibility is not guaranteed.

---

## Exceptions

### `EncryptionError`
Base exception for encryption-related failures.

### `DecryptionError`
Raised for unexpected decryption failures.

### `InvalidEncryptedData`
Raised when the encrypted payload is malformed, corrupted, or invalid.

### `InvalidEncryptionKey`
Raised when the provided password/key is invalid.

---