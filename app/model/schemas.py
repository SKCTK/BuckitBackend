from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

# Transaction schemas
class TransactionBase(BaseModel):
    user_id: int
    amount: float
    description: Optional[str] = None
    category: Optional[str] = None
    transaction_date: Optional[datetime] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    is_reconciled: Optional[bool] = False

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    transaction_date: Optional[datetime] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    is_reconciled: Optional[bool] = None

class Transaction(TransactionBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

# Income schemas
class IncomeBase(BaseModel):
    financial_summary_id: int
    salary: Optional[float] = 0
    investments: Optional[float] = 0
    business_income: Optional[float] = 0

class IncomeCreate(IncomeBase):
    pass

class IncomeUpdate(BaseModel):
    salary: Optional[float] = None
    investments: Optional[float] = None
    business_income: Optional[float] = None

class Income(IncomeBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

# Financial Summary schemas
class FinancialSummaryBase(BaseModel):
    user_id: int
    savings_balance: Optional[float] = 0
    investment_balance: Optional[float] = 0
    debt_balance: Optional[float] = 0

class FinancialSummaryCreate(FinancialSummaryBase):
    pass

class FinancialSummaryUpdate(BaseModel):
    savings_balance: Optional[float] = None
    investment_balance: Optional[float] = None
    debt_balance: Optional[float] = None

class FinancialSummary(FinancialSummaryBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

# Expenses schemas
class ExpensesBase(BaseModel):
    financial_summary_id: int
    rent_mortgage: Optional[float] = 0
    utilities: Optional[float] = 0
    insurance: Optional[float] = 0
    loan_payments: Optional[float] = 0
    groceries: Optional[float] = 0
    transportation: Optional[float] = 0
    subscriptions: Optional[float] = 0
    entertainment: Optional[float] = 0

class ExpensesCreate(ExpensesBase):
    pass

class ExpensesUpdate(BaseModel):
    rent_mortgage: Optional[float] = None
    utilities: Optional[float] = None
    insurance: Optional[float] = None
    loan_payments: Optional[float] = None
    groceries: Optional[float] = None
    transportation: Optional[float] = None
    subscriptions: Optional[float] = None
    entertainment: Optional[float] = None

class Expenses(ExpensesBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

# Bucket schemas
class BucketBase(BaseModel):
    user_id: int
    name: str
    target_amount: Optional[float] = 0
    current_saved_amount: Optional[float] = 0
    priority_score: Optional[int] = 1
    deadline: Optional[datetime] = None
    status: Optional[str] = "active"

class BucketCreate(BucketBase):
    pass

class BucketUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_saved_amount: Optional[float] = None
    priority_score: Optional[int] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None

class Bucket(BucketBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }
    
    def __init__(self, db):
        super().__init__()
        self.db = db 
