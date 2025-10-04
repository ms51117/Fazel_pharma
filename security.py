# app/core/security.py

from passlib.context import CryptContext

# Create a CryptContext instance for password hashing.
# We specify "bcrypt" as the hashing scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    :param plain_password: The password in plain text.
    :param hashed_password: The hashed password from the database.
    :return: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain password using bcrypt.

    :param password: The password in plain text.
    :return: The hashed password.
    """
    return pwd_context.hash(password)
