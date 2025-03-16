from sqlalchemy.orm import Session
from ..model import models, schemas

def get_bucket(db: Session, bucket_id: int):
    return db.query(models.Bucket).filter(models.Bucket.id == bucket_id).first()

def create_bucket(db: Session, bucket: schemas.BucketCreate):
    db_bucket = models.Bucket(**bucket.dict())
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

def update_bucket(db: Session, bucket_id: int, bucket: schemas.BucketUpdate):
    db_bucket = get_bucket(db, bucket_id=bucket_id)
    if not db_bucket:
        return None
    
    for var, value in vars(bucket).items():
        if value is not None:
            setattr(db_bucket, var, value)
    
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

def delete_bucket(db: Session, bucket_id: int):
    db_bucket = get_bucket(db, bucket_id=bucket_id)
    if not db_bucket:
        return None
    db.delete(db_bucket)
    db.commit()
    return db_bucket
