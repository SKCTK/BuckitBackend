from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..model import models, schemas
import logging

logger = logging.getLogger(__name__)

def get_bucket(db: Session, bucket_id: int):
    try:
        return db.query(models.Bucket).filter(models.Bucket.id == bucket_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_bucket: {str(e)}")
        raise

def get_user_buckets(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all buckets for a specific user with pagination"""
    try:
        # First verify the user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Attempted to get buckets for non-existent user {user_id}")
            raise ValueError(f"User with ID {user_id} does not exist")
            
        # Include ORDER BY for MSSQL pagination
        return db.query(models.Bucket).filter(
            models.Bucket.user_id == user_id
        ).order_by(models.Bucket.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_buckets: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in get_user_buckets: {str(e)}")
        raise

def create_bucket(db: Session, bucket: schemas.BucketCreate):
    try:
        # Validate user_id exists
        user = db.query(models.User).filter(models.User.id == bucket.user_id).first()
        if not user:
            logger.warning(f"Attempted to create bucket for non-existent user {bucket.user_id}")
            raise ValueError(f"User with ID {bucket.user_id} does not exist")
        
        db_bucket = models.Bucket(**bucket.model_dump())
        db.add(db_bucket)
        db.commit()
        db.refresh(db_bucket)
        logger.info(f"Created bucket with ID {db_bucket.id}")
        return db_bucket
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_bucket: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in create_bucket: {str(e)}")
        db.rollback()
        raise

def update_bucket(db: Session, bucket_id: int, bucket: schemas.BucketUpdate):
    try:
        db_bucket = get_bucket(db, bucket_id=bucket_id)
        if not db_bucket:
            logger.warning(f"Attempted to update non-existent bucket {bucket_id}")
            return None
        
        for var, value in vars(bucket).items():
            if value is not None:
                setattr(db_bucket, var, value)
        
        db.commit()
        db.refresh(db_bucket)
        logger.info(f"Updated bucket with ID {bucket_id}")
        return db_bucket
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_bucket: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in update_bucket: {str(e)}")
        db.rollback()
        raise

def delete_bucket(db: Session, bucket_id: int):
    try:
        db_bucket = get_bucket(db, bucket_id=bucket_id)
        if not db_bucket:
            logger.warning(f"Attempted to delete non-existent bucket {bucket_id}")
            return None
        
        db.delete(db_bucket)
        db.commit()
        logger.info(f"Deleted bucket with ID {bucket_id}")
        return db_bucket
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_bucket: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in delete_bucket: {str(e)}")
        db.rollback()
        raise
