from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..model import models, schemas
import logging

logger = logging.getLogger(__name__)

def get_income(db: Session, income_id: int):
    try:
        return db.query(models.Income).filter(models.Income.id == income_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_income: {str(e)}")
        raise

def get_income_by_financial_summary(db: Session, financial_summary_id: int):
    """Get income for a specific financial summary"""
    try:
        return db.query(models.Income).filter(
            models.Income.financial_summary_id == financial_summary_id
        ).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_income_by_financial_summary: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in get_income_by_financial_summary: {str(e)}")
        raise

def create_income(db: Session, income: schemas.IncomeCreate):
    try:
        # Check if income already exists for this financial summary
        existing_income = get_income_by_financial_summary(db, income.financial_summary_id)
        if existing_income:
            logger.warning(f"Financial summary {income.financial_summary_id} already has income (ID: {existing_income.id})")
            raise ValueError(f"Financial summary with ID {income.financial_summary_id} already has income")
        
        db_income = models.Income(**income.model_dump())
        db.add(db_income)
        db.commit()
        db.refresh(db_income)
        logger.info(f"Created income with ID {db_income.id}")
        return db_income
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_income: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in create_income: {str(e)}")
        db.rollback()
        raise

def update_income(db: Session, income_id: int, income: schemas.IncomeUpdate):
    try:
        db_income = get_income(db, income_id=income_id)
        if not db_income:
            logger.warning(f"Attempted to update non-existent income {income_id}")
            return None
        
        for var, value in vars(income).items():
            if value is not None:
                setattr(db_income, var, value)
        
        db.commit()
        db.refresh(db_income)
        logger.info(f"Updated income with ID {income_id}")
        return db_income
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_income: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in update_income: {str(e)}")
        db.rollback()
        raise

def delete_income(db: Session, income_id: int):
    try:
        db_income = get_income(db, income_id=income_id)
        if not db_income:
            logger.warning(f"Attempted to delete non-existent income {income_id}")
            return None
        
        db.delete(db_income)
        db.commit()
        logger.info(f"Deleted income with ID {income_id}")
        return db_income
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_income: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in delete_income: {str(e)}")
        db.rollback()
        raise
