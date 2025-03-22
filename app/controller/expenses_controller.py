from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..model import models, schemas
import logging

logger = logging.getLogger(__name__)

def get_expenses(db: Session, expenses_id: int):
    try:
        return db.query(models.Expenses).filter(models.Expenses.id == expenses_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_expenses: {str(e)}")
        raise

def get_expenses_by_financial_summary(db: Session, financial_summary_id: int):
    """Get expenses for a specific financial summary"""
    try:
        return db.query(models.Expenses).filter(
            models.Expenses.financial_summary_id == financial_summary_id
        ).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_expenses_by_financial_summary: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in get_expenses_by_financial_summary: {str(e)}")
        raise

def create_expenses(db: Session, expenses: schemas.ExpensesCreate):
    try:
        # Check if expenses already exist for this financial summary
        existing_expenses = get_expenses_by_financial_summary(db, expenses.financial_summary_id)
        if (existing_expenses):
            logger.warning(f"Financial summary {expenses.financial_summary_id} already has expenses (ID: {existing_expenses.id})")
            raise ValueError(f"Financial summary with ID {expenses.financial_summary_id} already has expenses")
        
        db_expenses = models.Expenses(**expenses.model_dump())
        db.add(db_expenses)
        db.commit()
        db.refresh(db_expenses)
        logger.info(f"Created expenses with ID {db_expenses.id}")
        return db_expenses
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_expenses: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in create_expenses: {str(e)}")
        db.rollback()
        raise

def update_expenses(db: Session, expenses_id: int, expenses: schemas.ExpensesUpdate):
    try:
        db_expenses = get_expenses(db, expenses_id=expenses_id)
        if not db_expenses:
            logger.warning(f"Attempted to update non-existent expenses {expenses_id}")
            return None
        
        for var, value in vars(expenses).items():
            if value is not None:
                setattr(db_expenses, var, value)
        
        db.commit()
        db.refresh(db_expenses)
        logger.info(f"Updated expenses with ID {expenses_id}")
        return db_expenses
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_expenses: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in update_expenses: {str(e)}")
        db.rollback()
        raise

def delete_expenses(db: Session, expenses_id: int):
    try:
        db_expenses = get_expenses(db, expenses_id=expenses_id)
        if not db_expenses:
            logger.warning(f"Attempted to delete non-existent expenses {expenses_id}")
            return None
        
        db.delete(db_expenses)
        db.commit()
        logger.info(f"Deleted expenses with ID {expenses_id}")
        return db_expenses
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_expenses: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in delete_expenses: {str(e)}")
        db.rollback()
        raise
