import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


class CryptoService:
    def __init__(self) -> None:
        raw = settings.ENCRYPTION_KEY
        # Add padding to make length a multiple of 4, then decode
        padded = raw + "=" * (-len(raw) % 4)
        key_bytes = base64.urlsafe_b64decode(padded)
        if len(key_bytes) < 32:
            raise ValueError("ENCRYPTION_KEY must decode to at least 32 bytes")
        self._key = key_bytes[:32]

    def encrypt(self, plaintext: str) -> str:
        nonce = os.urandom(12)
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()

    def decrypt(self, encrypted: str) -> str:
        padded = encrypted + "=" * (-len(encrypted) % 4)
        data = base64.urlsafe_b64decode(padded)
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(self._key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
