from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(255), nullable=False)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # One-to-one relationship with FinancialSummary
    financial_summary = relationship("FinancialSummary", back_populates="user", uselist=False)
    
    # One-to-many relationships with Bucket and Transaction
    buckets = relationship("Bucket", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class FinancialSummary(Base):
    __tablename__ = "financial_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    savings_balance = Column(Float, default=0)
    investment_balance = Column(Float, default=0)
    debt_balance = Column(Float, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # One-to-one relationships
    income = relationship("Income", back_populates="financial_summary", uselist=False)
    expenses = relationship("Expenses", back_populates="financial_summary", uselist=False)
    
    user = relationship("User", back_populates="financial_summary")

class Income(Base):
    __tablename__ = "incomes"
    
    id = Column(Integer, primary_key=True, index=True)
    salary = Column(Float, default=0)
    investments = Column(Float, default=0)
    business_income = Column(Float, default=0)
    financial_summary_id = Column(Integer, ForeignKey("financial_summaries.id"), unique=True, nullable=False)
    
    financial_summary = relationship("FinancialSummary", back_populates="income")

class Expenses(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    rent_mortgage = Column(Float, default=0)
    utilities = Column(Float, default=0)
    insurance = Column(Float, default=0)
    loan_payments = Column(Float, default=0)
    groceries = Column(Float, default=0)
    transportation = Column(Float, default=0)
    subscriptions = Column(Float, default=0)
    entertainment = Column(Float, default=0)
    financial_summary_id = Column(Integer, ForeignKey("financial_summaries.id"), unique=True, nullable=False)
    
    financial_summary = relationship("FinancialSummary", back_populates="expenses")

class Bucket(Base):
    __tablename__ = "buckets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, default=0)
    current_saved_amount = Column(Float, default=0)
    priority_score = Column(Integer, default=1)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")
    
    user = relationship("User", back_populates="buckets")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    reference = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)
    is_reconciled = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="transactions")