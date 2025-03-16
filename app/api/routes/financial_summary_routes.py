from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...controller import financial_summary_controller
from ...model import schemas
from ...database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.FinancialSummary)
def create_financial_summary(financial_summary: schemas.FinancialSummaryCreate, db: Session = Depends(get_db)):
    return financial_summary_controller.create_financial_summary(db=db, financial_summary=financial_summary)

@router.get("/{financial_summary_id}", response_model=schemas.FinancialSummary)
def read_financial_summary(financial_summary_id: int, db: Session = Depends(get_db)):
    db_financial_summary = financial_summary_controller.get_financial_summary(db, financial_summary_id=financial_summary_id)
    if db_financial_summary is None:
        raise HTTPException(status_code=404, detail="FinancialSummary not found")
    return db_financial_summary

@router.put("/{financial_summary_id}", response_model=schemas.FinancialSummary)
def update_financial_summary(financial_summary_id: int, financial_summary: schemas.FinancialSummaryUpdate, db: Session = Depends(get_db)):
    db_financial_summary = financial_summary_controller.get_financial_summary(db, financial_summary_id=financial_summary_id)
    if db_financial_summary is None:
        raise HTTPException(status_code=404, detail="FinancialSummary not found")
    return financial_summary_controller.update_financial_summary(db, financial_summary_id, financial_summary)

@router.delete("/{financial_summary_id}", response_model=schemas.FinancialSummary)
def delete_financial_summary(financial_summary_id: int, db: Session = Depends(get_db)):
    db_financial_summary = financial_summary_controller.get_financial_summary(db, financial_summary_id=financial_summary_id)
    if db_financial_summary is None:
        raise HTTPException(status_code=404, detail="FinancialSummary not found")
    return financial_summary_controller.delete_financial_summary(db, financial_summary_id=financial_summary_id)
