import pytest

def test_create_expenses(client, test_financial_summary):
    """Test creating expenses."""
    response = client.post(
        "/expenses/",
        json={
            "financial_summary_id": test_financial_summary.id,
            "rent_mortgage": 2000.0,
            "utilities": 300.0,
            "insurance": 200.0,
            "loan_payments": 400.0,
            "groceries": 500.0,
            "transportation": 150.0,
            "subscriptions": 50.0,
            "entertainment": 200.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rent_mortgage"] == 2000.0
    assert data["utilities"] == 300.0
    assert data["financial_summary_id"] == test_financial_summary.id
    assert "id" in data

def test_get_expenses(client, test_user, test_expenses):
    """Test getting expenses by ID."""
    response = client.get(f"/expenses/{test_expenses.id}?user_id={test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["rent_mortgage"] == test_expenses.rent_mortgage
    assert data["utilities"] == test_expenses.utilities
    assert data["id"] == test_expenses.id

def test_get_nonexistent_expenses(client, test_user):
    """Test getting expenses that don't exist."""
    response = client.get(f"/expenses/999?user_id={test_user.id}")
    assert response.status_code == 404
    assert "Expenses not found" in response.json()["detail"]

def test_update_expenses(client, test_user, test_expenses):
    """Test updating expenses."""
    response = client.put(
        f"/expenses/{test_expenses.id}?user_id={test_user.id}",
        json={
            "rent_mortgage": 2200.0,
            "utilities": 350.0,
            "groceries": 550.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rent_mortgage"] == 2200.0
    assert data["utilities"] == 350.0
    assert data["groceries"] == 550.0
    assert data["id"] == test_expenses.id

def test_update_nonexistent_expenses(client, test_user):
    """Test updating expenses that don't exist."""
    response = client.put(
        f"/expenses/999?user_id={test_user.id}",
        json={
            "rent_mortgage": 1500.0
        }
    )
    assert response.status_code == 404
    assert "Expenses not found" in response.json()["detail"]

def test_delete_expenses(client, test_user, test_expenses):
    """Test deleting expenses."""
    response = client.delete(f"/expenses/{test_expenses.id}?user_id={test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_expenses.id
    
    # Verify the expenses were deleted
    response = client.get(f"/expenses/{test_expenses.id}?user_id={test_user.id}")
    assert response.status_code == 404

def test_delete_nonexistent_expenses(client, test_user):
    """Test deleting expenses that don't exist."""
    response = client.delete(f"/expenses/999?user_id={test_user.id}")
    assert response.status_code == 404
    assert "Expenses not found" in response.json()["detail"]
