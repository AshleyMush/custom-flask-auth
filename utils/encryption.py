# Description: This file contains functions to hash and salt passwords and check if a password matches a hashed password.
from werkzeug.security import generate_password_hash, check_password_hash

def hash_and_salt_password(password):
    """This function hashes and salts the password using the werkzeug library and returns the hashed password.
    param password: The password to be hashed and salted (str)
    Returns: The hashed password (str)
        """
    return generate_password_hash(
        password,
        method='pbkdf2:sha256',
        salt_length=16
    )
    return password

def check_password(password, hashed_password):
    """This function checks if the password matches the hashed password.
    param password: The password to be checked (str)
    param hashed_password: The hashed password (str)
    Returns: True if the password matches the hashed password, False otherwise (bool)
    """
    return check_password_hash(hashed_password, password)
    return password