import pytest

def test_create_income(client, test_financial_summary):
    """Test creating income."""
    response = client.post(
        "/incomes/",
        json={
            "financial_summary_id": test_financial_summary.id,
            "salary": 6000.0,
            "investments": 500.0,
            "business_income": 1000.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["salary"] == 6000.0
    assert data["investments"] == 500.0
    assert data["business_income"] == 1000.0
    assert data["financial_summary_id"] == test_financial_summary.id
    assert "id" in data

def test_get_income(client, test_income):
    """Test getting income by ID."""
    response = client.get(f"/incomes/{test_income.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["salary"] == test_income.salary
    assert data["investments"] == test_income.investments
    assert data["id"] == test_income.id

def test_get_nonexistent_income(client):
    """Test getting income that doesn't exist."""
    response = client.get("/incomes/999")
    assert response.status_code == 404
    assert "Income not found" in response.json()["detail"]

def test_update_income(client, test_income):
    """Test updating income."""
    response = client.put(
        f"/incomes/{test_income.id}",
        json={
            "salary": 6500.0,
            "investments": 700.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["salary"] == 6500.0
    assert data["investments"] == 700.0
    assert data["id"] == test_income.id

def test_update_nonexistent_income(client):
    """Test updating income that doesn't exist."""
    response = client.put(
        "/incomes/999",
        json={
            "salary": 7000.0
        }
    )
    assert response.status_code == 404
    assert "Income not found" in response.json()["detail"]

def test_delete_income(client, test_income):
    """Test deleting income."""
    response = client.delete(f"/incomes/{test_income.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_income.id
    
    # Verify the income was deleted
    response = client.get(f"/incomes/{test_income.id}")
    assert response.status_code == 404

def test_delete_nonexistent_income(client):
    """Test deleting income that doesn't exist."""
    response = client.delete("/incomes/999")
    assert response.status_code == 404
    assert "Income not found" in response.json()["detail"]
