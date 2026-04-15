import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


class CryptoService:
    def __init__(self) -> None:
        key_bytes = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY + "==")
        self._key = key_bytes[:32]

    def encrypt(self, plaintext: str) -> str:
        nonce = os.urandom(12)
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()

    def decrypt(self, encrypted: str) -> str:
        data = base64.urlsafe_b64decode(encrypted + "==")
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(self._key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
