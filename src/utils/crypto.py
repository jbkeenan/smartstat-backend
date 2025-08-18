import base64, os
from cryptography.fernet import Fernet, InvalidToken


def _fernet():
    key = os.getenv("SECRET_BOX_KEY")
    if not key:
        # 32 urlsafe base64 bytes; generate one locally then set in Render
        raise RuntimeError("SECRET_BOX_KEY not set")
    try:
        return Fernet(key)
    except Exception:
        return Fernet(base64.urlsafe_b64encode(key.encode()[:32]))


def encrypt(s: str | None) -> str | None:
    if s is None:
        return None
    return _fernet().encrypt(s.encode()).decode()


def decrypt(s: str | None) -> str | None:
    if s is None:
        return None
    try:
        return _fernet().decrypt(s.encode()).decode()
    except InvalidToken:
        return None
