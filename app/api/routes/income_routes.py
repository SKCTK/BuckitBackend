from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...controller import income_controller
from ...model import schemas
from ...database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Income)
def create_income(income: schemas.IncomeCreate, db: Session = Depends(get_db)):
    return income_controller.create_income(db=db, income=income)

@router.get("/{income_id}", response_model=schemas.Income)
def read_income(income_id: int, db: Session = Depends(get_db)):
    db_income = income_controller.get_income(db, income_id=income_id)
    if db_income is None:
        raise HTTPException(status_code=404, detail="Income not found")
    return db_income

@router.put("/{income_id}", response_model=schemas.Income)
def update_income(income_id: int, income: schemas.IncomeUpdate, db: Session = Depends(get_db)):
    db_income = income_controller.get_income(db, income_id=income_id)
    if db_income is None:
        raise HTTPException(status_code=404, detail="Income not found")
    return income_controller.update_income(db, income_id, income)

@router.delete("/{income_id}", response_model=schemas.Income)
def delete_income(income_id: int, db: Session = Depends(get_db)):
    db_income = income_controller.get_income(db, income_id=income_id)
    if db_income is None:
        raise HTTPException(status_code=404, detail="Income not found")
    return income_controller.delete_income(db, income_id=income_id)
