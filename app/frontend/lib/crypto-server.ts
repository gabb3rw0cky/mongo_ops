import crypto from "crypto";

/**
 * Internal shape for derived key material.
 */
type KeyAndIV = {
  key: Buffer
  iv: Buffer
}

const ENCRYPTION_KEY = process.env.NEXT_PUBLIC_ENCRYPTION_KEY || "";
/**
 * Legacy OpenSSL "Salted__" prefix used by EVP_BytesToKey-compatible payloads.
 */
const OPENSSL_SALTED_PREFIX = "Salted__";

/**
 * AES-256-GCM settings.
 */
const KEY_LENGTH_BYTES = 32;
const SALT_START_INDEX= 8;
const SALT_END_INDEX= 16;


/**
 * Encrypts a JSON-serializable value using AES-256-GCM.
 *
 * Output format:
 *   v1:<base64(salt)>:<base64(iv)>:<base64(authTag)>:<base64(ciphertext)>
 *
 * This format provides:
 * - confidentiality
 * - integrity/authentication
 * - versioning for future migrations
 *
 * @param {T} data JSON-serializable value to encrypt
 * @returns {string} Encrypted payload string
 */
export function encryptPayload<T>(data: T): string {
  const jsonString = JSON.stringify(data);

  // Generate random salt (8 bytes)
  const salt = crypto.randomBytes(SALT_START_INDEX);

  // Derive key and IV using OpenSSL EVP_BytesToKey (MD5-based)

  const { key, iv } = evpBytesToKey(ENCRYPTION_KEY, salt, KEY_LENGTH_BYTES, SALT_END_INDEX);

  // Encrypt with AES-256-CBC
  const cipher = crypto.createCipheriv("aes-256-cbc", key, iv);
  let encrypted = cipher.update(jsonString, "utf8");
  encrypted = Buffer.concat([encrypted, cipher.final()]);

  // Format: "Salted__" + salt + ciphertext (OpenSSL compatible)
  const result = Buffer.concat([
    Buffer.from(OPENSSL_SALTED_PREFIX),
    salt,
    encrypted,
  ]);

  return result.toString("base64");
}

/**
 * Decrypts a payload produced by either:
 * 1. the modern AES-256-GCM format from encryptPayload()
 * 2. the legacy OpenSSL-compatible AES-256-CBC format using EVP_BytesToKey
 *
 * @param {string} encryptedData Encrypted payload string
 * @returns {T} Parsed JSON value
 */
export function decryptPayload(encryptedData: string): any {
  // Accepts data previously encrypted with encryptPayload or Python equivalent.
  const raw = Buffer.from(encryptedData, "base64");
  if (raw.slice(0, SALT_START_INDEX).toString() !== OPENSSL_SALTED_PREFIX) {
    throw new Error("Invalid encrypted data format");
  }

  const salt = raw.slice(SALT_START_INDEX, SALT_END_INDEX);
  const ciphertext = raw.slice(SALT_END_INDEX);

  const { key, iv } = evpBytesToKey(ENCRYPTION_KEY, salt, KEY_LENGTH_BYTES, SALT_END_INDEX);
  const decipher = crypto.createDecipheriv("aes-256-cbc", key, iv);
  let decrypted = decipher.update(ciphertext);
  decrypted = Buffer.concat([decrypted, decipher.final()]);

  return JSON.parse(decrypted.toString("utf8"));
}


/**
 * OpenSSL EVP_BytesToKey-compatible key derivation.
 *
 * @param {string} password Encryption key password
 * @param {Buffer} salt Encryption salt
 * @param {number} keyLen key length
 * @param {number} ivLen iv length
 * @returns {KeyAndIV} Parsed JSON value
 */
function evpBytesToKey(
  password: string,
  salt: Buffer,
  keyLen: number,
  ivLen: number
): KeyAndIV {
  let dtot = Buffer.alloc(0);
  let d = Buffer.alloc(0);
  const passwordBuf = Buffer.from(password);

  while (dtot.length < keyLen + ivLen) {
    d = crypto
      .createHash("md5")
      .update(Buffer.concat([d, passwordBuf, salt]))
      .digest();
    dtot = Buffer.concat([dtot, d]);
  }

  return {
    key: dtot.subarray(0, keyLen),
    iv: dtot.subarray(keyLen, keyLen + ivLen),
  };
}
