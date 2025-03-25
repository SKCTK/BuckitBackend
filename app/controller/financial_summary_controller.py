from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..model import models, schemas
import logging

logger = logging.getLogger(__name__)

def get_financial_summary(db: Session, financial_summary_id: int):
    try:
        return db.query(models.FinancialSummary).filter(models.FinancialSummary.id == financial_summary_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_financial_summary: {str(e)}")
        raise

def get_financial_summary_by_user(db: Session, user_id: int):
    """Get financial summary for a specific user"""
    try:
        # First verify the user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Attempted to get financial summary for non-existent user {user_id}")
            raise ValueError(f"User with ID {user_id} does not exist")
            
        return db.query(models.FinancialSummary).filter(models.FinancialSummary.user_id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_financial_summary_by_user: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in get_financial_summary_by_user: {str(e)}")
        raise

def create_financial_summary(db: Session, financial_summary: schemas.FinancialSummaryCreate):
    try:
        # Validate user_id exists
        user = db.query(models.User).filter(models.User.id == financial_summary.user_id).first()
        if not user:
            logger.warning(f"Attempted to create financial summary for non-existent user {financial_summary.user_id}")
            raise ValueError(f"User with ID {financial_summary.user_id} does not exist")
        
        # Check if the user already has a financial summary
        existing_summary = db.query(models.FinancialSummary).filter(
            models.FinancialSummary.user_id == financial_summary.user_id
        ).first()
        
        if existing_summary:
            logger.warning(f"User {financial_summary.user_id} already has a financial summary (ID: {existing_summary.id})")
            raise ValueError(f"User with ID {financial_summary.user_id} already has a financial summary")
        
        db_financial_summary = models.FinancialSummary(**financial_summary.model_dump())
        db.add(db_financial_summary)
        db.commit()
        db.refresh(db_financial_summary)
        logger.info(f"Created financial summary with ID {db_financial_summary.id}")
        return db_financial_summary
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_financial_summary: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in create_financial_summary: {str(e)}")
        db.rollback()
        raise

def update_financial_summary(db: Session, financial_summary_id: int, financial_summary: schemas.FinancialSummaryUpdate):
    try:
        db_financial_summary = get_financial_summary(db, financial_summary_id=financial_summary_id)
        if not db_financial_summary:
            logger.warning(f"Attempted to update non-existent financial summary {financial_summary_id}")
            return None
        
        for var, value in vars(financial_summary).items():
            if value is not None:
                setattr(db_financial_summary, var, value)
        
        db.commit()
        db.refresh(db_financial_summary)
        logger.info(f"Updated financial summary with ID {financial_summary_id}")
        return db_financial_summary
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_financial_summary: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in update_financial_summary: {str(e)}")
        db.rollback()
        raise

def delete_financial_summary(db: Session, financial_summary_id: int):
    try:
        db_financial_summary = get_financial_summary(db, financial_summary_id=financial_summary_id)
        if not db_financial_summary:
            logger.warning(f"Attempted to delete non-existent financial summary {financial_summary_id}")
            return None
        
        db.delete(db_financial_summary)
        db.commit()
        logger.info(f"Deleted financial summary with ID {financial_summary_id}")
        return db_financial_summary
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_financial_summary: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in delete_financial_summary: {str(e)}")
        db.rollback()
        raise
