from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ...controller import expenses_controller, financial_summary_controller
from ...model import schemas
from ...database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Expenses)
def create_expenses(expenses: schemas.ExpensesCreate, db: Session = Depends(get_db)):
    try:
        # Validate financial summary exists and belongs to the right user
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=expenses.financial_summary_id
        )
        if not financial_summary:
            raise HTTPException(status_code=404, detail="Financial summary not found")
        
        return expenses_controller.create_expenses(db=db, expenses=expenses)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error creating expenses: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating expenses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user/{user_id}", response_model=schemas.Expenses)
def read_user_expenses(
    user_id: int = Path(..., description="The ID of the user to get expenses for"),
    db: Session = Depends(get_db)
):
    """Get expenses for a specific user"""
    try:
        # First get the user's financial summary
        financial_summary = financial_summary_controller.get_financial_summary_by_user(db, user_id=user_id)
        if not financial_summary:
            raise HTTPException(status_code=404, detail=f"Financial summary not found for user {user_id}")
        
        # Then get the expenses for that financial summary
        expenses = expenses_controller.get_expenses_by_financial_summary(
            db, financial_summary_id=financial_summary.id
        )
        if not expenses:
            raise HTTPException(status_code=404, detail=f"Expenses not found for user {user_id}")
            
        return expenses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving expenses for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{expenses_id}", response_model=schemas.Expenses)
def read_expenses(
    expenses_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_expenses = expenses_controller.get_expenses(db, expenses_id=expenses_id)
        if db_expenses is None:
            raise HTTPException(status_code=404, detail="Expenses not found")
        
        # Get financial summary to verify user authorization
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=db_expenses.financial_summary_id
        )
        
        # Verify expenses belong to the user through financial summary
        if financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access expenses {expenses_id} belonging to user {financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access these expenses")
            
        return db_expenses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving expenses {expenses_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{expenses_id}", response_model=schemas.Expenses)
def update_expenses(
    expenses_id: int,
    expenses: schemas.ExpensesUpdate,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_expenses = expenses_controller.get_expenses(db, expenses_id=expenses_id)
        if db_expenses is None:
            raise HTTPException(status_code=404, detail="Expenses not found")
        
        # Get financial summary to verify user authorization
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=db_expenses.financial_summary_id
        )
        
        # Verify expenses belong to the user through financial summary
        if financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to update expenses {expenses_id} belonging to user {financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update these expenses")
            
        return expenses_controller.update_expenses(db, expenses_id, expenses)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating expenses {expenses_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating expenses {expenses_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{expenses_id}", response_model=schemas.Expenses)
def delete_expenses(
    expenses_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        db_expenses = expenses_controller.get_expenses(db, expenses_id=expenses_id)
        if db_expenses is None:
            raise HTTPException(status_code=404, detail="Expenses not found")
        
        # Get financial summary to verify user authorization
        financial_summary = financial_summary_controller.get_financial_summary(
            db, financial_summary_id=db_expenses.financial_summary_id
        )
        
        # Verify expenses belong to the user through financial summary
        if financial_summary.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete expenses {expenses_id} belonging to user {financial_summary.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete these expenses")
            
        return expenses_controller.delete_expenses(db, expenses_id=expenses_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting expenses {expenses_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error deleting expenses {expenses_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
