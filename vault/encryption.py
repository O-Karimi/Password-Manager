import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_master_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

def generate_user_keys(password: str):
    salt = os.urandom(16)
    master_key = derive_master_key(password, salt)
    
    vault_key = Fernet.generate_key() 
    
    f = Fernet(master_key)
    encrypted_vault_key = f.encrypt(vault_key)
    
    return salt, encrypted_vault_key

def unlock_vault_key(password: str, salt: bytes, encrypted_vault_key: bytes) -> bytes:
    master_key = derive_master_key(password, salt)
    f = Fernet(master_key)
    return f.decrypt(encrypted_vault_key)

def encrypt_password(plain_text: str, vault_key: str) -> str:
    f = Fernet(vault_key.encode('utf-8'))
    encrypted_bytes = f.encrypt(plain_text.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_password(encrypted_str: str, vault_key: str) -> str:
    f = Fernet(vault_key.encode('utf-8'))
    decrypted_bytes = f.decrypt(encrypted_str.encode('utf-8'))
    return decrypted_bytes.decode('utf-8')