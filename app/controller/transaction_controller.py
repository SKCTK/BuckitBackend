from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..model import models, schemas
import logging

logger = logging.getLogger(__name__)

def get_transaction(db: Session, transaction_id: int):
    try:
        return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_transaction: {str(e)}")
        raise

def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all transactions for a specific user with pagination"""
    try:
        # First verify the user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Attempted to get transactions for non-existent user {user_id}")
            raise ValueError(f"User with ID {user_id} does not exist")
            
        # Include an ORDER BY clause to make OFFSET/LIMIT work with MSSQL
        return db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id
        ).order_by(models.Transaction.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_transactions: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in get_user_transactions: {str(e)}")
        raise

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    try:
        # Validate user_id exists
        user = db.query(models.User).filter(models.User.id == transaction.user_id).first()
        if not user:
            logger.warning(f"Attempted to create transaction for non-existent user {transaction.user_id}")
            raise ValueError(f"User with ID {transaction.user_id} does not exist")
        
        db_transaction = models.Transaction(**transaction.model_dump())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        logger.info(f"Created transaction with ID {db_transaction.id}")
        return db_transaction
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_transaction: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in create_transaction: {str(e)}")
        db.rollback()
        raise

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    try:
        db_transaction = get_transaction(db, transaction_id=transaction_id)
        if not db_transaction:
            logger.warning(f"Attempted to update non-existent transaction {transaction_id}")
            return None
        
        for var, value in vars(transaction).items():
            if value is not None:
                setattr(db_transaction, var, value)
        
        db.commit()
        db.refresh(db_transaction)
        logger.info(f"Updated transaction with ID {transaction_id}")
        return db_transaction
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_transaction: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in update_transaction: {str(e)}")
        db.rollback()
        raise

def delete_transaction(db: Session, transaction_id: int):
    try:
        db_transaction = get_transaction(db, transaction_id=transaction_id)
        if not db_transaction:
            logger.warning(f"Attempted to delete non-existent transaction {transaction_id}")
            return None
        
        db.delete(db_transaction)
        db.commit()
        logger.info(f"Deleted transaction with ID {transaction_id}")
        return db_transaction
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_transaction: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in delete_transaction: {str(e)}")
        db.rollback()
        raise
