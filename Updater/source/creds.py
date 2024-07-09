"""
This module provides functions to encrypt and decrypt the API key used to access the GitHub API.

Functions:
- generate_key(password: str) -> bytes: Generates a key from the given password.
- decrypt(token: bytes, key: bytes) -> str: Decrypts the given token using the key.
- get_api_key() -> str: Returns the decrypted API key.

Constants:
- PASSWORD: The password used to generate the key.
- SALT: The salt used to generate the key.
"""

import logging
import base64
import pickle
import os
from source.path import APPLICATION_DIR
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

# TODO: Find a better way to enter these values for development to prevent leak
PASSWORD = r"e0097c6a06cb15177ae73f1757001a86e4a7afe762481bafd0fcac9ac3a7b365"
SALT = r"e0097c6a06cb1517"


def generate_key() -> bytes:
    """
    Generates a key from the given password.

    Returns:
    - bytes: The generated key.
    """
    password = PASSWORD.encode()
    salt = SALT.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))

    return key


def decrypt(token: bytes, key: bytes) -> str:
    """
    Decrypts the given token using the key.

    Parameters:
    - token (bytes): The token to decrypt.
    - key (bytes): The key to use for decryption.

    Returns:
    - str: The decrypted data.
    """
    f = Fernet(key)
    data = f.decrypt(token)

    return data.decode()


def get_api_key():
    """
    Returns the decrypted API key.
    
    Returns:
    - str: The decrypted API key.
    """
    try:
        with open(os.path.join(APPLICATION_DIR, "creds"), "rb") as f:
            token = pickle.load(f)
    except FileNotFoundError:
        logger.critical("API key file not found")
        return None
    try:
        key = generate_key()
    except Exception:
        logger.critical("Failed to generate key")
        return None
    try:
        decrypted_token = decrypt(token, key)
    except Exception:
        logger.critical("Failed to decrypt API key")
        return None

    return decrypted_token
