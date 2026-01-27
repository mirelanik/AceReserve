"""Password hashing and verification utilities.
Provides secure password hashing and verification using pwdlib.
"""

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password.
    Args:
        plain_password: The plain text password to verify.
        hashed_password: The stored hashed password.
    Returns:
        bool: True if passwords match, False otherwise.
    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain text password.
    Args:
        password: The plain text password to hash.
    Returns:
        str: The hashed password string.
    """
    return password_hash.hash(password)
