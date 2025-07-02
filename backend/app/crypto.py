import os
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

_SECRET = os.getenv("DATA_ENCRYPTION_KEY", "raw_data_secret")
_KEY = base64.urlsafe_b64encode(hashlib.sha256(_SECRET.encode()).digest())
_FERNET = Fernet(_KEY)


def encrypt(value: str) -> str:
    return _FERNET.encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    try:
        return _FERNET.decrypt(value.encode()).decode()
    except InvalidToken:
        return value
