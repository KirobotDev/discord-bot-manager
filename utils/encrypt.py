from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import getpass

def derive_key(password):
    salt = b'salt_discord_bot_manager'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def get_master_password():
    return getpass.getpass("Enter master password: ")

def encrypt_token(token, password):
    key = derive_key(password)
    fernet = Fernet(key)
    return fernet.encrypt(token.encode())

def decrypt_token(encrypted, password):
    key = derive_key(password)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted).decode()