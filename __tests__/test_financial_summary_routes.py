import pytest

def test_create_financial_summary(client, test_user):
    """Test creating a financial summary."""
    response = client.post(
        "/financial-summaries/",
        json={
            "user_id": test_user.id,
            "savings_balance": 3000.0,
            "investment_balance": 7000.0,
            "debt_balance": 2000.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["savings_balance"] == 3000.0
    assert data["investment_balance"] == 7000.0
    assert data["debt_balance"] == 2000.0
    assert data["user_id"] == test_user.id
    assert "id" in data

def test_get_financial_summary(client, test_user, test_financial_summary):
    """Test getting a financial summary by ID."""
    response = client.get(f"/financial-summaries/{test_financial_summary.id}?user_id={test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["savings_balance"] == test_financial_summary.savings_balance
    assert data["investment_balance"] == test_financial_summary.investment_balance
    assert data["id"] == test_financial_summary.id

def test_get_nonexistent_financial_summary(client, test_user):
    """Test getting a financial summary that doesn't exist."""
    response = client.get(f"/financial-summaries/999?user_id={test_user.id}")
    assert response.status_code == 404
    assert "Financial summary not found" in response.json()["detail"]

def test_update_financial_summary(client, test_user, test_financial_summary):
    """Test updating a financial summary."""
    response = client.put(
        f"/financial-summaries/{test_financial_summary.id}?user_id={test_user.id}",
        json={
            "savings_balance": 3500.0,
            "investment_balance": 8000.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["savings_balance"] == 3500.0
    assert data["investment_balance"] == 8000.0
    assert data["id"] == test_financial_summary.id

def test_update_nonexistent_financial_summary(client, test_user):
    """Test updating a financial summary that doesn't exist."""
    response = client.put(
        f"/financial-summaries/999?user_id={test_user.id}",
        json={
            "savings_balance": 5000.0
        }
    )
    assert response.status_code == 404
    assert "Financial summary not found" in response.json()["detail"]

def test_delete_financial_summary(client, test_user, test_financial_summary):
    """Test deleting a financial summary."""
    response = client.delete(f"/financial-summaries/{test_financial_summary.id}?user_id={test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_financial_summary.id
    
    # Verify the financial summary was deleted
    response = client.get(f"/financial-summaries/{test_financial_summary.id}?user_id={test_user.id}")
    assert response.status_code == 404

def test_delete_nonexistent_financial_summary(client, test_user):
    """Test deleting a financial summary that doesn't exist."""
    response = client.delete(f"/financial-summaries/999?user_id={test_user.id}")
    assert response.status_code == 404
    assert "Financial summary not found" in response.json()["detail"]
