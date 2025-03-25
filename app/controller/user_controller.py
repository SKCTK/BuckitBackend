from sqlalchemy.orm import Session
from ..model import models, schemas
from ..core.security import get_password_hash
import os
import base64

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Generate a salt
    salt = os.urandom(32)
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    
    # Generate password hash with the salt
    import hashlib
    key = hashlib.pbkdf2_hmac(
        'sha256',
        user.password.encode('utf-8'),
        salt,
        100000  # number of iterations
    )
    password_hash = base64.b64encode(key).decode('utf-8')
    
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=password_hash,
        password_salt=salt_b64
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None
    
    for var, value in vars(user).items():
        if value is not None:
            setattr(db_user, var, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user
