from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ...controller import financial_summary_controller
from ...model import schemas
from ...database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.FinancialSummary)
def create_financial_summary(financial_summary: schemas.FinancialSummaryCreate, db: Session = Depends(get_db)):
    try:
        return financial_summary_controller.create_financial_summary(db=db, financial_summary=financial_summary)
    except SQLAlchemyError as e:
        logger.error(f"Database error creating financial summary: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating financial summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user/{user_id}", response_model=schemas.FinancialSummary)
def read_user_financial_summary(
    user_id: int = Path(..., description="The ID of the user to get financial summary for"),
    db: Session = Depends(get_db)
):
    """Get financial summary for a specific user"""
    try:
        db_financial_summary = financial_summary_controller.get_financial_summary_by_user(db, user_id=user_id)
        if db_financial_summary is None:
            raise HTTPException(status_code=404, detail=f"Financial summary not found for user {user_id}")
        return db_financial_summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving financial summary for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{financial_summary_id}", response_model=schemas.FinancialSummary)
def read_financial_summary(
    financial_summary_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_financial_summary = financial_summary_controller.get_financial_summary(db, financial_summary_id=financial_summary_id)
        if db_financial_summary is None:
            raise HTTPException(status_code=404, detail="Financial summary not found")
        
        # Verify financial summary belongs to the user
        if db_financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access financial summary {financial_summary_id} belonging to user {db_financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this financial summary")
            
        return db_financial_summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving financial summary {financial_summary_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{financial_summary_id}", response_model=schemas.FinancialSummary)
def update_financial_summary(
    financial_summary_id: int,
    financial_summary: schemas.FinancialSummaryUpdate,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_financial_summary = financial_summary_controller.get_financial_summary(db, financial_summary_id=financial_summary_id)
        if db_financial_summary is None:
            raise HTTPException(status_code=404, detail="Financial summary not found")
        
        # Verify financial summary belongs to the user
        if db_financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to update financial summary {financial_summary_id} belonging to user {db_financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this financial summary")
            
        return financial_summary_controller.update_financial_summary(db, financial_summary_id, financial_summary)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating financial summary {financial_summary_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating financial summary {financial_summary_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{financial_summary_id}", response_model=schemas.FinancialSummary)
def delete_financial_summary(
    financial_summary_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_financial_summary = financial_summary_controller.get_financial_summary(db, financial_summary_id=financial_summary_id)
        if db_financial_summary is None:
            raise HTTPException(status_code=404, detail="Financial summary not found")
        
        # Verify financial summary belongs to the user
        if db_financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete financial summary {financial_summary_id} belonging to user {db_financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this financial summary")
            
        return financial_summary_controller.delete_financial_summary(db, financial_summary_id=financial_summary_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting financial summary {financial_summary_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error deleting financial summary {financial_summary_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
