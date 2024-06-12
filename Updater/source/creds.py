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
- API_KEY: The GitHub API key. Not included in plain text.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import pickle
import os

PASSWORD = r"HominumServer123!"
API_KEY = r""


def generate_key(password: str) -> bytes:
    """
    Generates a key from the given password.

    Parameters:
    - password (str): The password to generate the key from.

    Returns:
    - bytes: The generated key.
    """
    password = password.encode()
    salt = password[::-1]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt(data: str, key: bytes) -> bytes:
    """
    Encrypts the given data using the key.
    
    Parameters:
    - data (str): The data to encrypt.
    - key (bytes): The key to use for encryption.
    
    Returns:
    - bytes: The encrypted data.
    """
    data = data.encode()
    f = Fernet(key)
    return f.encrypt(data)


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


def dump_file():
    """
    Dumps the encrypted API key to a file.

    Returns:
    - None
    """
    key = generate_key(PASSWORD)
    encrypted_key = encrypt(API_KEY, key)
    with open("creds.pkl", "wb") as f:
        pickle.dump(encrypted_key.decode(), f)


def get_api_key():
    """
    Returns the decrypted API key.
    
    Returns:
    - str: The decrypted API key.
    """
    from source.path import APPLICATION_PATH

    with open(os.path.join(APPLICATION_PATH, "creds.pkl"), "rb") as f:
        encrypted_key = pickle.load(f)
    key = generate_key(PASSWORD)
    return decrypt(encrypted_key, key)


if __name__ == "__main__":
    # dump_file()
    pass
