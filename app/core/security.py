"""
Password hashing and JWT token creation/verification.
Passwords are never stored in plain text — only their bcrypt hash.
JWTs let the API verify who is calling it without hitting the database
on every single request (the user's identity + role travel inside the token).
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password for storage in the database."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain-text password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT containing the given claims (e.g. user id, org id, role),
    with an expiry time attached.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT. Raises jwt.PyJWTError if the token is invalid,
    tampered with, or expired — the caller is responsible for handling that.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])