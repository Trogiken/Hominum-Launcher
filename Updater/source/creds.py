from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import pickle
import os

PASSWORD = r"HominumServer123!"
API_KEY = r""


def generate_key(password):
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


def encrypt(data, key):
    data = data.encode()
    f = Fernet(key)
    return f.encrypt(data)


def decrypt(token, key):
    f = Fernet(key)
    data = f.decrypt(token)
    return data.decode()


def dump_file():
    key = generate_key(PASSWORD)
    encrypted_key = encrypt(API_KEY, key)
    with open("creds.pkl", "wb") as f:
        pickle.dump(encrypted_key.decode(), f)


def get_api_key():
    from source.path import APPLICATION_PATH

    with open(os.path.join(APPLICATION_PATH, "creds.pkl"), "rb") as f:
        encrypted_key = pickle.load(f)
    key = generate_key(PASSWORD)
    return decrypt(encrypted_key, key)


if __name__ == "__main__":
    #dump_file()
    pass
