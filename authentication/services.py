import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

class EncryptionService:
    def __init__(self):
        encoded_key = os.environ["ENCRYPTION_KEY"]
        key = base64.urlsafe_b64decode(encoded_key)

        self.aes = AESGCM(key)

    def encrypt(self, value: str) -> bytes:
        nonce = os.urandom(12)

        ciphertext = self.aes.encrypt(
            nonce,
            value.encode("utf-8"),
            None
        )

        return nonce + ciphertext

    def decrypt(self, encrypted_value: bytes) -> str:
        nonce = encrypted_value[:12]
        ciphertext = encrypted_value[12:]

        plaintext = self.aes.decrypt(
            nonce,
            ciphertext,
            None
        )

        return plaintext.decode("utf-8")

    def encrypt_user_data(self, data: dict) -> dict:
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "country",
            "city",
            "current_activity",
        ]

        encrypted_data = data.copy()

        for field in fields:
            encrypted_data[field] = self.encrypt(
                str(data[field])
            )

        return encrypted_data