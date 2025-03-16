from sqlalchemy.orm import Session
from ...model import models, schemas

def get_financial_summary(db: Session, financial_summary_id: int):
    return db.query(models.FinancialSummary).filter(models.FinancialSummary.id == financial_summary_id).first()

def create_financial_summary(db: Session, financial_summary: schemas.FinancialSummaryCreate):
    db_financial_summary = models.FinancialSummary(**financial_summary.dict())
    db.add(db_financial_summary)
    db.commit()
    db.refresh(db_financial_summary)
    return db_financial_summary

def update_financial_summary(db: Session, financial_summary_id: int, financial_summary: schemas.FinancialSummaryUpdate):
    db_financial_summary = get_financial_summary(db, financial_summary_id=financial_summary_id)
    if not db_financial_summary:
        return None
    
    for var, value in vars(financial_summary).items():
        if value is not None:
            setattr(db_financial_summary, var, value)
    
    db.commit()
    db.refresh(db_financial_summary)
    return db_financial_summary

def delete_financial_summary(db: Session, financial_summary_id: int):
    db_financial_summary = get_financial_summary(db, financial_summary_id=financial_summary_id)
    if not db_financial_summary:
        return None
    db.delete(db_financial_summary)
    db.commit()
    return db_financial_summary
