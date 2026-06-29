import secrets
import string

def generate_strong_password(length=16):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    
    secure_password = ''.join(secrets.choice(characters) for _ in range(length))
    return secure_password