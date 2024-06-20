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

import base64
import pickle
import os
from source.path import APPLICATION_DIR
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

PASSWORD = r""
SALT = r""


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
    with open(os.path.join(APPLICATION_DIR, "creds"), "rb") as f:
        token = pickle.load(f)
    key = generate_key()
    decrypted_token = decrypt(token, key)

    return decrypted_token
