import hashlib
import secrets


def generate_password_hash():
    return secrets.token_urlsafe(16)

def hash_password(password: str, salt: str):
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_password(password: str, salt: str, password_hash: str):
    return hash_password(password, salt) == password_hash
