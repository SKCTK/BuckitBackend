import pytest
from datetime import datetime, UTC

def test_create_transaction(client, test_user):
    """Test creating a transaction."""
    response = client.post(
        "/transactions/",
        json={
            "user_id": test_user.id,
            "amount": 75.50,
            "description": "Dinner",
            "category": "Food",
            "transaction_date": datetime.now(UTC).isoformat(),
            "reference": "T98765",
            "notes": "Restaurant",
            "is_reconciled": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 75.5
    assert data["description"] == "Dinner"
    assert data["category"] == "Food"
    assert "id" in data

def test_get_transaction(client, test_user, test_transaction):
    """Test getting a transaction by ID."""
    response = client.get(f"/transactions/{test_transaction.id}?user_id={test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == test_transaction.amount
    assert data["description"] == test_transaction.description
    assert data["id"] == test_transaction.id

def test_get_nonexistent_transaction(client, test_user):
    """Test getting a transaction that doesn't exist."""
    response = client.get(f"/transactions/999?user_id={test_user.id}")
    assert response.status_code == 404
    assert "Transaction not found" in response.json()["detail"]

def test_update_transaction(client, test_user, test_transaction):
    """Test updating a transaction."""
    response = client.put(
        f"/transactions/{test_transaction.id}?user_id={test_user.id}",
        json={
            "amount": 85.75,
            "description": "Updated Dinner",
            "category": "Dining"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 85.75
    assert data["description"] == "Updated Dinner"
    assert data["category"] == "Dining"
    assert data["id"] == test_transaction.id

def test_update_nonexistent_transaction(client, test_user):
    """Test updating a transaction that doesn't exist."""
    response = client.put(
        f"/transactions/999?user_id={test_user.id}",
        json={
            "amount": 100.0
        }
    )
    assert response.status_code == 404
    assert "Transaction not found" in response.json()["detail"]

def test_delete_transaction(client, test_user, test_transaction):
    """Test deleting a transaction."""
    response = client.delete(f"/transactions/{test_transaction.id}?user_id={test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_transaction.id
    
    # Verify the transaction was deleted
    response = client.get(f"/transactions/{test_transaction.id}?user_id={test_user.id}")
    assert response.status_code == 404

def test_delete_nonexistent_transaction(client, test_user):
    """Test deleting a transaction that doesn't exist."""
    response = client.delete(f"/transactions/999?user_id={test_user.id}")
    assert response.status_code == 404
    assert "Transaction not found" in response.json()["detail"]
