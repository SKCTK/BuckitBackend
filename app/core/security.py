import hashlib
import os
import base64
from datetime import datetime, timedelta, UTC
from typing import Optional, Tuple
import os
from jose import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    # This function is now used differently - the salt is handled in user_controller
    # Kept for backwards compatibility with tests
    salt = os.urandom(32)  # 32 bytes = 256 bits
    
    # Hash the password with the salt
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # number of iterations
    )
    
    # Return the hash as a base64-encoded string
    key_b64 = base64.b64encode(key).decode('utf-8')
    return key_b64

def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against a hash."""
    # Decode the salt from base64
    salt_bytes = base64.b64decode(salt)
    
    # Hash the plain password with the salt
    key = hashlib.pbkdf2_hmac(
        'sha256',
        plain_password.encode('utf-8'),
        salt_bytes,
        100000  # same number of iterations as in get_password_hash
    )
    
    # Encode the key in base64
    computed_hash = base64.b64encode(key).decode('utf-8')
    
    # Compare the computed hash with the stored hash
    return computed_hash == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
