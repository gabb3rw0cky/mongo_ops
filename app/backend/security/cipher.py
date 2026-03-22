from    .cipher_errors          import  EncryptionError
from    .cipher_errors          import  InvalidEncryptedData
from    .cipher_errors          import  DecryptionError
from    .cipher_errors          import  InvalidEncryptionKey
from    .cipher_errors          import  EVP_BytesToKeyError
from    Crypto.Util.Padding     import  unpad
from    Crypto.Util.Padding     import  pad
from    Crypto.Cipher           import  AES 
from    typing                  import  Dict, Tuple, Any
import  hashlib
import  base64
import  json
import  os

SALT_PREFIX     =   b"Salted__"
PREFIX_SIZE     =   len(SALT_PREFIX)
SALT_SIZE       =   8
AES_KEY_SIZE    =   32  # AES-256
AES_BLOCK_SIZE  =   16
MIN_LENGTH      =   len(SALT_PREFIX) + SALT_SIZE + AES_BLOCK_SIZE

def _evp_bytes_to_key(
    password    :   bytes,
    salt        :   bytes,
    key_len     :   int,
    iv_len      :   int,
) -> Tuple[bytes, bytes]:
    """
    Derive key and IV using OpenSSL's legacy EVP_BytesToKey algorithm.

    This function is compatible with CryptoJS/OpenSSL password-based AES-CBC
    encryption that uses the "Salted__" header format.

    Args:
        password (bytes): Password bytes used for derivation.
        salt (bytes): 8-byte salt.
        key_len (int): Required key length in bytes.
        iv_len (int): Required IV length in bytes.

    Returns:
        Tuple: A tuple of (key, iv).

    Raises:
        EVP_BytesToKeyError: If salt is empty or sizes are invalid.
    """
    if not password:
        raise EVP_BytesToKeyError("Password must not be empty.")
    if len(salt) != SALT_SIZE:
        raise EVP_BytesToKeyError(f"Salt must be exactly {SALT_SIZE} bytes.")
    if key_len <= 0 or iv_len <= 0:
        raise EVP_BytesToKeyError("key_len and iv_len must be positive integers.")

    try:
        derived = b""
        block = b""

        while len(derived) < key_len + iv_len:
            block = hashlib.md5(block + password + salt).digest()
            derived += block

        return derived[:key_len], derived[key_len:key_len + iv_len]
    except Exception as e: 
        raise   EVP_BytesToKeyError(e)

def _validate_string(encrypted: str) -> str:
    """
    Validate and normalize an encrypted base64 string.

    Args:
        encrypted (str): Base64-encoded encrypted payload.

    Returns:
        str: Stripped encrypted string.

    Raises:
        InvalidEncryptedData: If input is not a non-empty string.
    """
    if not isinstance(encrypted, str) or not encrypted.strip():
        raise InvalidEncryptedData("Encrypted data must be a none empty string.")
    return  encrypted.strip()

def _decode_base64(data: str) -> bytes:
    """
    Decode a base64 string with strict validation.

    Args:
        data (str): Base64-encoded string.

    Returns:
        bytes: Decoded bytes.

    Raises:
        InvalidEncryptedData: If data is not valid base64.
    """
    try:
        return  base64.b64decode(data)
    except Exception as e:
        raise   InvalidEncryptedData("Encrypted data is not valid base64.")

def encode_base64(data: bytes) -> str:
    """
    Encode bytes as a base64 UTF-8 string.

    Args:
        data (bytes): Raw bytes.

    Returns:
        str: Base64-encoded string.

    Raises:
        EncryptionError: If encoding fails.
    """
    try:
        return  base64.b64encode(data).decode("utf-8")
    except Exception as e:
        raise   EncryptionError("Can not encode to base64.")
    
def _parse_openssl_payload(raw: bytes) -> Tuple[bytes, bytes]:
    """
    Parse an OpenSSL-compatible encrypted payload.

    Expected format:
        b"Salted__" + 8-byte salt + ciphertext

    Args:
        raw (bytes): Decoded encrypted bytes.

    Returns:
        Tuple: A tuple of (salt, ciphertext).

    Raises:
        InvalidEncryptedData: If payload format is invalid.
    """
    if len(raw) < MIN_LENGTH:
                raise InvalidEncryptedData("Encrypted data is too short.")

    if not raw.startswith(SALT_PREFIX):
        raise InvalidEncryptedData(
            "Invalid encrypted data format: missing OpenSSL salt header."
        )

    start_index =   PREFIX_SIZE
    end_index   =   PREFIX_SIZE+SALT_SIZE
    salt        =   raw[start_index:end_index]
    ciphertext  =   raw[end_index:]

    return  salt, ciphertext

def _decrypt_aes_cbc(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypt AES-CBC ciphertext and remove PKCS#7 padding.

    Args:
        key (bytes): AES key.
        iv (bytes): AES IV.
        ciphertext (bytes): Encrypted bytes.

    Returns:
        bytes: Decrypted plaintext bytes.

    Raises:
        InvalidEncryptedData: If ciphertext is malformed or decryption fails.
    """
    if len(ciphertext) == 0 or len(ciphertext) % AES_BLOCK_SIZE != 0:
        raise InvalidEncryptedData("Ciphertext length is invalid for AES-CBC.")
    
    try:
        cipher  =   AES.new(key, AES.MODE_CBC, iv)
        return  unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    except ValueError:
        raise InvalidEncryptedData(
            "Decryption failed. The key may be incorrect or the data may be corrupted."
        )
    
def _encrypt_aes_cbc(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """
    Encrypt plaintext using AES-CBC with PKCS#7 padding.

    Args:
        key (bytes): AES key.
        iv (bytes): AES IV.
        plaintext: Plaintext bytes.

    Returns:
        bytes: Ciphertext bytes.

    Raises:
        EncryptionError: If encryption fails.
    """
    try:
    # Encrypt with AES-256-CBC using pycryptodome so decryption is compatible
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Pad the plaintext to a multiple of the block size
        padded = pad(plaintext, AES.block_size)
        # padded = pad(plaintext.encode('utf-8'), AES.block_size)

        return  cipher.encrypt(padded)
    except Exception as e:
        EncryptionError(e)

def _deserialize_json(data: bytes) -> Dict[str, Any]:
    """
    Deserialize UTF-8 JSON bytes into a dictionary.

    Args:
        data (bytes): UTF-8 JSON bytes.

    Returns:
        Dict: Parsed dictionary.

    Raises:
        InvalidEncryptedData: If JSON is invalid or not a JSON object.
    """
    try:
        return  json.loads(data.decode("utf-8"))
    except Exception:
        raise InvalidEncryptedData("Decrypted payload is not valid UTF-8 JSON.") 
    
def _serialize_json(data: Dict[str, Any])->bytes:
    """
    Serialize a mapping to compact UTF-8 JSON bytes.

    Args:
        data (Dict): Dictionary-like object to serialize.

    Returns:
        bytes: UTF-8 JSON bytes.

    Raises:
        EncryptionError: If data is not serializable.
    """
    try:
        return  json.dumps(data).encode("utf-8")
    except Exception:
        raise InvalidEncryptedData("Decrypted payload is not valid UTF-8 JSON.") 


class   Cipher():
    """
    Encrypt and decrypt JSON payloads in a CryptoJS/OpenSSL-compatible format.
    """

    def __init__(self, key: str) -> None:
        """
        Initialize the encryption helper.

        Args:
            key (str): Password string used to derive AES key and IV.

        Raises:
            InvalidEncryptionKey: If the key is empty or key is not a string.
        """

        if not key or not isinstance(key, str):
            raise InvalidEncryptionKey("key must be a none empty string")

        self._password = key.encode("utf-8")

    def decrypt_payload(self, encrypted: str) -> Dict:
        """
        Decrypt a CryptoJS/OpenSSL-compatible encrypted payload.

        Args:
            encrypted (str): Base64-encoded payload in the format
                base64("Salted__" + salt + ciphertext)

        Returns:
            Dict: The decrypted JSON object as a dictionary.

        Raises:
            InvalidEncryptedData: If the payload is malformed or cannot be
                decrypted correctly.
            DecryptionError: If an unexpected error occurs during decryption.
        """
        if not isinstance(encrypted, str) or not encrypted.strip():
            raise InvalidEncryptedData("Encrypted data must be a none empty string.")
        
        try:
            encrypted   =   _validate_string(encrypted)

            raw         =   _decode_base64(encrypted)

            salt, text  =   _parse_openssl_payload(raw)

            key, iv     =   _evp_bytes_to_key(
                password    =   self._password,
                salt        =   salt,
                key_len     =   AES_KEY_SIZE,
                iv_len      =   AES_BLOCK_SIZE,
            )

            decrypted   =   _decrypt_aes_cbc(key, iv, text)

            return  _deserialize_json(decrypted)
    
        except InvalidEncryptedData:
            raise

        except  EVP_BytesToKeyError:
            raise
    
        except Exception as e:
            raise   DecryptionError(e)

    def encrypt_payload(self, data: Dict) -> str:
        """
        Encrypt a dictionary-like payload using CryptoJS/OpenSSL-compatible AES-CBC.

        The returned string is base64-encoded and contains:
            b"Salted__" + 8-byte random salt + ciphertext

        Args:
            data (Dict): Dictionary-like payload to encrypt.

        Returns:
            str: Base64-encoded encrypted string.

        Raises:
            EncryptionError: If serialization or encryption fails.
        """
        try:

            json_string     =   _serialize_json(data)
            # Generate random salt (8 bytes)
            salt            =   os.urandom(SALT_SIZE)


            # Derive key and IV using OpenSSL EVP_BytesToKey (MD5-based)
            key, iv         =   _evp_bytes_to_key(
                password    =   self._password,
                salt        =   salt,
                key_len     =   AES_KEY_SIZE,
                iv_len      =   AES_BLOCK_SIZE,
            )

            encrypted       =   _encrypt_aes_cbc(key, iv, json_string)

            result          =   SALT_PREFIX + salt + encrypted

            return encode_base64(result)
    
        except EncryptionError:
            raise

        except  EVP_BytesToKeyError:
            raise
    
        except Exception as e:
            raise   EncryptionError(e)
