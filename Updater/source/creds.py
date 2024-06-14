"""
This module provides functions to encrypt and decrypt the API key used to access the GitHub API.

Functions:
- generate_key(password: str) -> bytes: Generates a key from the given password.
- encrypt(data: str, key: bytes) -> bytes: Encrypts the given data using the key.
- decrypt(token: bytes, key: bytes) -> str: Decrypts the given token using the key.
- dump_file() -> None: Dumps the encrypted API key to a file.
- get_api_key() -> str: Returns the decrypted API key.

Constants:
- PASSWORD: The password used to generate the key.
- SALT: The salt used to generate the key.
- API_KEY: The GitHub API key. Not included in plain text.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import pickle
import os

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
    from source.path import APPLICATION_PATH

    with open(os.path.join(APPLICATION_PATH, "creds"), "rb") as f:
        token = pickle.load(f)
    key = generate_key()
    return decrypt(token, key)
