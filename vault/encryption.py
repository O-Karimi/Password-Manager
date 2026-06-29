from cryptography.fernet import Fernet
from django.conf import settings

def get_fernet():
    key = settings.ENCRYPTION_KEY.encode("utf-8")
    return Fernet(key)

def encrypt_password(plain_text_password: str) -> str:
    f = get_fernet()
    encrypted_bytes = f.encrypt(plain_text_password.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt_password(encrypted_password_str: str) -> str:
    f = get_fernet()
    decrypted_bytes = f.decrypt(encrypted_password_str.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")