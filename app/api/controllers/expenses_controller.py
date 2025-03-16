from sqlalchemy.orm import Session
from ...model import models, schemas

def get_expenses(db: Session, expenses_id: int):
    return db.query(models.Expenses).filter(models.Expenses.id == expenses_id).first()

def create_expenses(db: Session, expenses: schemas.ExpensesCreate):
    db_expenses = models.Expenses(**expenses.dict())
    db.add(db_expenses)
    db.commit()
    db.refresh(db_expenses)
    return db_expenses

def update_expenses(db: Session, expenses_id: int, expenses: schemas.ExpensesUpdate):
    db_expenses = get_expenses(db, expenses_id=expenses_id)
    if not db_expenses:
        return None
    
    for var, value in vars(expenses).items():
        if value is not None:
            setattr(db_expenses, var, value)
    
    db.commit()
    db.refresh(db_expenses)
    return db_expenses

def delete_expenses(db: Session, expenses_id: int):
    db_expenses = get_expenses(db, expenses_id=expenses_id)
    if not db_expenses:
        return None
    db.delete(db_expenses)
    db.commit()
    return db_expenses
