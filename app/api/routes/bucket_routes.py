from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ...controller import bucket_controller
from ...model import schemas
from ...database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Bucket)
def create_bucket(bucket: schemas.BucketCreate, db: Session = Depends(get_db)):
    try:
        return bucket_controller.create_bucket(db=db, bucket=bucket)
    except SQLAlchemyError as e:
        logger.error(f"Database error creating bucket: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating bucket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user/{user_id}", response_model=list[schemas.Bucket])
def read_user_buckets(
    user_id: int = Path(..., description="The ID of the user to get buckets for"),
    skip: int = Query(0, description="Skip N buckets"),
    limit: int = Query(100, description="Limit the number of buckets returned"),
    db: Session = Depends(get_db)
):
    """Get all buckets for a specific user"""
    try:
        return bucket_controller.get_user_buckets(db, user_id=user_id, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving buckets for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{bucket_id}", response_model=schemas.Bucket)
def read_bucket(
    bucket_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_bucket = bucket_controller.get_bucket(db, bucket_id=bucket_id)
        if db_bucket is None:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Verify bucket belongs to the user
        if db_bucket.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access bucket {bucket_id} belonging to user {db_bucket.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this bucket")
            
        return db_bucket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving bucket {bucket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{bucket_id}", response_model=schemas.Bucket)
def update_bucket(
    bucket_id: int,
    bucket: schemas.BucketUpdate,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_bucket = bucket_controller.get_bucket(db, bucket_id=bucket_id)
        if db_bucket is None:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Verify bucket belongs to the user
        if db_bucket.user_id != user_id:
            logger.warning(f"User {user_id} attempted to update bucket {bucket_id} belonging to user {db_bucket.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this bucket")
            
        return bucket_controller.update_bucket(db, bucket_id, bucket)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating bucket {bucket_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating bucket {bucket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{bucket_id}", response_model=schemas.Bucket)
def delete_bucket(
    bucket_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_bucket = bucket_controller.get_bucket(db, bucket_id=bucket_id)
        if db_bucket is None:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Verify bucket belongs to the user
        if db_bucket.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete bucket {bucket_id} belonging to user {db_bucket.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this bucket")
            
        return bucket_controller.delete_bucket(db, bucket_id=bucket_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting bucket {bucket_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error deleting bucket {bucket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
