from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...controller import user_controller
from ...model import schemas
from ...database import get_db
import logging

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = user_controller.get_user_by_email(db, email=user.email)
        if db_user is not None:
            # Return HTTPException directly instead of raising it
            raise HTTPException(status_code=400, detail="Email already registered")
        return user_controller.create_user(db=db, user=user)
    except HTTPException as he:
        # Re-raise HTTP exceptions directly
        logging.warning(f"HTTP Exception in create_user: {he.status_code}: {he.detail}")
        raise
    except Exception as e:
        # Log other unexpected errors
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_controller.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_controller.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_controller.update_user(db, user_id, user)

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_controller.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_controller.delete_user(db, user_id=user_id)
