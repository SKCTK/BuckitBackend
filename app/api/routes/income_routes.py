from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ...controller import income_controller, financial_summary_controller
from ...model import schemas
from ...database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Income)
def create_income(income: schemas.IncomeCreate, db: Session = Depends(get_db)):
    try:
        # Validate financial summary exists and belongs to the right user
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=income.financial_summary_id
        )
        if not financial_summary:
            raise HTTPException(status_code=404, detail="Financial summary not found")
        
        return income_controller.create_income(db=db, income=income)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error creating income: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating income: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user/{user_id}", response_model=schemas.Income)
def read_user_income(
    user_id: int = Path(..., description="The ID of the user to get income for"),
    db: Session = Depends(get_db)
):
    """Get income for a specific user"""
    try:
        # First get the user's financial summary
        financial_summary = financial_summary_controller.get_financial_summary_by_user(db, user_id=user_id)
        if not financial_summary:
            raise HTTPException(status_code=404, detail=f"Financial summary not found for user {user_id}")
        
        # Then get the income for that financial summary
        income = income_controller.get_income_by_financial_summary(
            db, financial_summary_id=financial_summary.id
        )
        if not income:
            raise HTTPException(status_code=404, detail=f"Income not found for user {user_id}")
            
        return income
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving income for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{income_id}", response_model=schemas.Income)
def read_income(
    income_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_income = income_controller.get_income(db, income_id=income_id)
        if db_income is None:
            raise HTTPException(status_code=404, detail="Income not found")
        
        # Get financial summary to verify user authorization
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=db_income.financial_summary_id
        )
        
        # Verify income belongs to the user through financial summary
        if financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access income {income_id} belonging to user {financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this income")
            
        return db_income
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving income {income_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{income_id}", response_model=schemas.Income)
def update_income(
    income_id: int,
    income: schemas.IncomeUpdate,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_income = income_controller.get_income(db, income_id=income_id)
        if db_income is None:
            raise HTTPException(status_code=404, detail="Income not found")
        
        # Get financial summary to verify user authorization
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=db_income.financial_summary_id
        )
        
        # Verify income belongs to the user through financial summary
        if financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to update income {income_id} belonging to user {financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this income")
            
        return income_controller.update_income(db, income_id, income)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating income {income_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating income {income_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{income_id}", response_model=schemas.Income)
def delete_income(
    income_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_income = income_controller.get_income(db, income_id=income_id)
        if db_income is None:
            raise HTTPException(status_code=404, detail="Income not found")
        
        # Get financial summary to verify user authorization
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=db_income.financial_summary_id
        )
        
        # Verify income belongs to the user through financial summary
        if financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete income {income_id} belonging to user {financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this income")
            
        return income_controller.delete_income(db, income_id=income_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting income {income_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error deleting income {income_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
