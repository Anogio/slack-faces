from cryptography.fernet import Fernet
import json
from cachetools import cached, LRUCache
from constants import ENCRYPTION_KEY


@cached(cache=LRUCache(maxsize=128))
def encrypt(message: str) -> bytes:
    return Fernet(ENCRYPTION_KEY).encrypt(message.encode())


@cached(cache=LRUCache(maxsize=128))
def decrypt(token: bytes) -> str:
    return Fernet(ENCRYPTION_KEY).decrypt(token).decode()


def encrypt_dict(d: dict) -> str:
    return encrypt(json.dumps(d)).decode()


def decrypt_dict(s: str) -> dict:
    return json.loads(decrypt(s.encode()))
