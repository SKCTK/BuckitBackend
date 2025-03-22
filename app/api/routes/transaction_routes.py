from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ...controller import transaction_controller
from ...model import schemas
from ...database import get_db
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    try:
        return transaction_controller.create_transaction(db=db, transaction=transaction)
    except SQLAlchemyError as e:
        logger.error(f"Database error creating transaction: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user/{user_id}", response_model=list[schemas.Transaction])
def read_user_transactions(
    user_id: int = Path(..., description="The ID of the user to get transactions for"),
    skip: int = Query(0, description="Skip N transactions"),
    limit: int = Query(100, description="Limit the number of transactions returned"),
    db: Session = Depends(get_db)
):
    """Get all transactions for a specific user"""
    try:
        return transaction_controller.get_user_transactions(db, user_id=user_id, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving transactions for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(
    transaction_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        # Get transaction and verify it belongs to the user
        db_transaction = transaction_controller.get_transaction(db, transaction_id=transaction_id)
        if db_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Verify transaction belongs to the user
        if db_transaction.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access transaction {transaction_id} belonging to user {db_transaction.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this transaction")
            
        return db_transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(
    transaction_id: int,
    transaction: schemas.TransactionUpdate,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        # Get transaction and verify it belongs to the user
        db_transaction = transaction_controller.get_transaction(db, transaction_id=transaction_id)
        if db_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Verify transaction belongs to the user
        if db_transaction.user_id != user_id:
            logger.warning(f"User {user_id} attempted to update transaction {transaction_id} belonging to user {db_transaction.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this transaction")
            
        return transaction_controller.update_transaction(db, transaction_id, transaction)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating transaction {transaction_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(
    transaction_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    try:
        # Get transaction and verify it belongs to the user
        db_transaction = transaction_controller.get_transaction(db, transaction_id=transaction_id)
        if db_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Verify transaction belongs to the user
        if db_transaction.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete transaction {transaction_id} belonging to user {db_transaction.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")
            
        return transaction_controller.delete_transaction(db, transaction_id=transaction_id)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting transaction {transaction_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
