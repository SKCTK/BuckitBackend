from sqlalchemy.orm import Session
from ..model import models, schemas

def get_income(db: Session, income_id: int):
    return db.query(models.Income).filter(models.Income.id == income_id).first()

def create_income(db: Session, income: schemas.IncomeCreate):
    db_income = models.Income(**income.model_dump())
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income

def update_income(db: Session, income_id: int, income: schemas.IncomeUpdate):
    db_income = get_income(db, income_id=income_id)
    if not db_income:
        return None
    
    for var, value in vars(income).items():
        if value is not None:
            setattr(db_income, var, value)
    
    db.commit()
    db.refresh(db_income)
    return db_income

def delete_income(db: Session, income_id: int):
    db_income = get_income(db, income_id=income_id)
    if not db_income:
        return None
    db.delete(db_income)
    db.commit()
    return db_income
