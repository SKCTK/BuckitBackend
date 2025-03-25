from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Get database URL from environment or use a default for development
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback mechanism: If SQL Server connection fails, use SQLite
# This helps during development and testing
if not DATABASE_URL:
    # First try to connect to SQL Server with environment variables
    DB_USER = os.getenv("DB_USER", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "YourStrong!Passw0rd")
    DB_SERVER = os.getenv("DB_SERVER", "localhost")
    DB_PORT = os.getenv("DB_PORT", "1433")
    DB_NAME = os.getenv("DB_NAME", "FinanceApp")
    
    try:
        DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
        # Test connection - will raise exception if can't connect
        test_engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 5})
        with test_engine.connect() as conn:
            pass
        logging.info("Successfully connected to SQL Server")
    except Exception as e:
        logging.warning(f"SQL Server connection failed: {e}. Falling back to SQLite.")
        # Fallback to SQLite if SQL Server connection fails
        DATABASE_URL = "sqlite:///./finance_app.db"

# Create SQLAlchemy engine - now with error handling for both SQL Server and SQLite
try:
    if "sqlite" in DATABASE_URL:
        engine = create_engine(
            DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
        # Enable foreign key support for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        engine = create_engine(DATABASE_URL)
    
    logging.info(f"Using database: {DATABASE_URL}")
except Exception as e:
    logging.error(f"Database engine creation failed: {e}")
    # Last resort fallback to in-memory SQLite
    logging.warning("Using in-memory SQLite as last resort")
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
