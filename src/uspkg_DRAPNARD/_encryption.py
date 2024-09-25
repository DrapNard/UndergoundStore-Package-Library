import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib

AES_BLOCK_SIZE = 16

def _generate_key_from_uid(uid: str):
    return hashlib.sha256(uid.encode()).digest()

def _encrypt_data(key, data):
    iv = secrets.token_bytes(AES_BLOCK_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize(), iv

def _decrypt_data(key, iv, encrypted_data):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()
