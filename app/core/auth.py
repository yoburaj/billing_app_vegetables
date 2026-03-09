
import os
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from base64 import b64encode, b64decode

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.database.database import get_db
from app.models.user import User, UserRole
from app.core import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

AES_KEY_HEX = config.AES_KEY
if not AES_KEY_HEX:
    # Fallback to a random key if not set, though it should be set
    AES_KEY = os.urandom(32)
else:
    AES_KEY = bytes.fromhex(AES_KEY_HEX)

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# --- Password Hashing Logic ---

def hash_password_sync(password: str) -> str:
    """Synchronous version of password hashing."""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    hashed_password = kdf.derive(password.encode())
    return b64encode(salt + hashed_password).decode('utf-8')

async def hash_password(password: str) -> str:
    """Asynchronous wrapper for password hashing."""
    return await asyncio.to_thread(hash_password_sync, password)

def verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    """Synchronous version of password verification."""
    try:
        decoded = b64decode(hashed_password.encode('utf-8'))
        salt, stored_hash = decoded[:16], decoded[16:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        kdf.verify(plain_password.encode(), stored_hash)
        return True
    except Exception:
        return False

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Asynchronous wrapper for password verification."""
    return await asyncio.to_thread(verify_password_sync, plain_password, hashed_password)

# Aliases for compatibility with existing code
def get_password_hash(password: str) -> str:
    return hash_password_sync(password)

def verify_password_compat(plain_password: str, hashed_password: str) -> bool:
    return verify_password_sync(plain_password, hashed_password)


# --- Phone Hashing/Encryption Logic ---

def hash_phone_sync(phone: str) -> str:
    """One-way hash for phone number."""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    hashed_phone = kdf.derive(phone.encode())
    return b64encode(salt + hashed_phone).decode('utf-8')

async def hash_phone(phone: str) -> str:
    return await asyncio.to_thread(hash_phone_sync, phone)

async def encrypt_phone(phone: str) -> str:
    if not isinstance(phone, str):
        phone = str(phone)
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)
    encrypted_data = aesgcm.encrypt(nonce, phone.encode(), None)
    return b64encode(nonce + encrypted_data).decode("utf-8")

async def decrypt_phone(encrypted_phone: str) -> str:
    try:
        aesgcm = AESGCM(AES_KEY)
        encrypted_data = b64decode(encrypted_phone)
        nonce, ciphertext = encrypted_data[:12], encrypted_data[12:]
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_data.decode("utf-8")
    except Exception:
        return encrypted_phone


# --- JWT Logic ---

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


def check_role(roles: List[UserRole]):
    def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions"
            )
        return current_user

    return role_checker
