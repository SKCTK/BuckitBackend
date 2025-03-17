import sys
from pathlib import Path
import pytest
import os
from dotenv import load_dotenv

# Load test environment variables from __tests__/.env.test
test_env_path = Path(__file__).parent / ".env.test"
load_dotenv(test_env_path)

# Add the project root directory to the Python path properly
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Now that we've added the path, we can import from app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.model.models import Base  # Import Base from models directly
from app.database import get_db
from app.main import app

# Use in-memory SQLite for testing - updated to store in __tests__ directory
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./__tests__/test.db")

@pytest.fixture
def test_db():
    """Create a fresh database for each test."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Create a db session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Create a test client with the test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    
    # Remove the override after the test
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    from app.model import models
    from app.core.security import get_password_hash
    import base64
    import os
    
    # Generate a salt
    salt = os.urandom(32)
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    
    user = models.User(
        name="Test User", 
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        password_salt=salt_b64
    )
    
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_financial_summary(test_db, test_user):
    """Create a test financial summary."""
    from app.model import models
    
    financial_summary = models.FinancialSummary(
        user_id=test_user.id,
        savings_balance=1000.0,
        investment_balance=2000.0,
        debt_balance=500.0
    )
    
    test_db.add(financial_summary)
    test_db.commit()
    test_db.refresh(financial_summary)
    return financial_summary

@pytest.fixture
def test_income(test_db, test_financial_summary):
    """Create a test income."""
    from app.model import models
    
    income = models.Income(
        financial_summary_id=test_financial_summary.id,
        salary=5000.0,
        investments=200.0,
        business_income=300.0
    )
    
    test_db.add(income)
    test_db.commit()
    test_db.refresh(income)
    return income

@pytest.fixture
def test_expenses(test_db, test_financial_summary):
    """Create a test expenses."""
    from app.model import models
    
    expenses = models.Expenses(
        financial_summary_id=test_financial_summary.id,
        rent_mortgage=1500.0,
        utilities=200.0,
        insurance=150.0,
        groceries=400.0
    )
    
    test_db.add(expenses)
    test_db.commit()
    test_db.refresh(expenses)
    return expenses

@pytest.fixture
def test_bucket(test_db, test_user):
    """Create a test bucket."""
    from app.model import models
    from datetime import datetime, timedelta, UTC
    
    bucket = models.Bucket(
        user_id=test_user.id,
        name="Vacation",
        target_amount=1000.0,
        current_saved_amount=250.0,
        priority_score=2,
        deadline=datetime.now(UTC) + timedelta(days=90),
        status="active"
    )
    
    test_db.add(bucket)
    test_db.commit()
    test_db.refresh(bucket)
    return bucket

@pytest.fixture
def test_transaction(test_db, test_user):
    """Create a test transaction."""
    from app.model import models
    from datetime import datetime, UTC
    
    transaction = models.Transaction(
        user_id=test_user.id,
        amount=150.0,
        description="Groceries",
        category="Food",
        transaction_date=datetime.now(UTC),
        reference="T12345",
        notes="Weekly shopping",
        is_reconciled=True
    )
    
    test_db.add(transaction)
    test_db.commit()
    test_db.refresh(transaction)
    return transaction
