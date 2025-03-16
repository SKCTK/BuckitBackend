from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use a default for development
DATABASE_URL = os.getenv("DATABASE_URL", "mssql+pyodbc://sa:azureaihack2025!@localhost:1433/FinancialBudgetApp?driver=ODBC+Driver+17+for+SQL+Server")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
