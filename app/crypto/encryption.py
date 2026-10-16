import os
import hmac
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, MultiFernet


@lru_cache(maxsize=1)
def get_fernet():
    current = os.environ["ENCRYPTION_KEY"]
    keys = [Fernet(current.encode())]

    old = os.getenv("ENCRYPTION_KEY_OLD")
    if old:
        keys.append(Fernet(old.encode()))

    return MultiFernet(keys)


def encrypt_field(value):
    if value is None:
        return None
    return get_fernet().encrypt(
        value.encode("utf-8")
    ).decode("ascii")


def decrypt_field(value):
    if value is None:
        return None
    return get_fernet().decrypt(
        value.encode("ascii")
    ).decode("utf-8")


def blind_index(value):
    key = os.environ["BLIND_INDEX_KEY"].encode()
    normalized = value.strip().lower().encode("utf-8")

    return hmac.new(
        key,
        normalized,
        hashlib.sha256
    ).hexdigest()
