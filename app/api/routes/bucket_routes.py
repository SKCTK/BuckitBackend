from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...controller import bucket_controller
from ...model import schemas
from ...database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Bucket)
def create_bucket(bucket: schemas.BucketCreate, db: Session = Depends(get_db)):
    return bucket_controller.create_bucket(db=db, bucket=bucket)

@router.get("/{bucket_id}", response_model=schemas.Bucket)
def read_bucket(bucket_id: int, db: Session = Depends(get_db)):
    db_bucket = bucket_controller.get_bucket(db, bucket_id=bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return db_bucket

@router.put("/{bucket_id}", response_model=schemas.Bucket)
def update_bucket(bucket_id: int, bucket: schemas.BucketUpdate, db: Session = Depends(get_db)):
    db_bucket = bucket_controller.get_bucket(db, bucket_id=bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return bucket_controller.update_bucket(db, bucket_id, bucket)

@router.delete("/{bucket_id}", response_model=schemas.Bucket)
def delete_bucket(bucket_id: int, db: Session = Depends(get_db)):
    db_bucket = bucket_controller.get_bucket(db, bucket_id=bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return bucket_controller.delete_bucket(db, bucket_id=bucket_id)
