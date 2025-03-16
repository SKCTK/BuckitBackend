from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...controller import expenses_controller
from ...model import schemas
from ...database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Expenses)
def create_expenses(expenses: schemas.ExpensesCreate, db: Session = Depends(get_db)):
    return expenses_controller.create_expenses(db=db, expenses=expenses)

@router.get("/{expenses_id}", response_model=schemas.Expenses)
def read_expenses(expenses_id: int, db: Session = Depends(get_db)):
    db_expenses = expenses_controller.get_expenses(db, expenses_id=expenses_id)
    if db_expenses is None:
        raise HTTPException(status_code=404, detail="Expenses not found")
    return db_expenses

@router.put("/{expenses_id}", response_model=schemas.Expenses)
def update_expenses(expenses_id: int, expenses: schemas.ExpensesUpdate, db: Session = Depends(get_db)):
    db_expenses = expenses_controller.get_expenses(db, expenses_id=expenses_id)
    if db_expenses is None:
        raise HTTPException(status_code=404, detail="Expenses not found")
    return expenses_controller.update_expenses(db, expenses_id, expenses)

@router.delete("/{expenses_id}", response_model=schemas.Expenses)
def delete_expenses(expenses_id: int, db: Session = Depends(get_db)):
    db_expenses = expenses_controller.get_expenses(db, expenses_id=expenses_id)
    if db_expenses is None:
        raise HTTPException(status_code=404, detail="Expenses not found")
    return expenses_controller.delete_expenses(db, expenses_id=expenses_id)
