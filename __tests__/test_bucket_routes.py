import pytest
from datetime import datetime, timedelta, UTC

def test_create_bucket(client, test_user):
    """Test creating a bucket."""
    deadline = datetime.now(UTC) + timedelta(days=180)
    response = client.post(
        "/buckets/",
        json={
            "user_id": test_user.id,
            "name": "New Car",
            "target_amount": 15000.0,
            "current_saved_amount": 5000.0,
            "priority_score": 3,
            "deadline": deadline.isoformat(),
            "status": "active"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Car"
    assert data["target_amount"] == 15000.0
    assert data["current_saved_amount"] == 5000.0
    assert "id" in data

def test_get_bucket(client, test_bucket):
    """Test getting a bucket by ID."""
    response = client.get(f"/buckets/{test_bucket.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_bucket.name
    assert data["target_amount"] == test_bucket.target_amount
    assert data["id"] == test_bucket.id

def test_get_nonexistent_bucket(client):
    """Test getting a bucket that doesn't exist."""
    response = client.get("/buckets/999")
    assert response.status_code == 404
    assert "Bucket not found" in response.json()["detail"]

def test_update_bucket(client, test_bucket):
    """Test updating a bucket."""
    response = client.put(
        f"/buckets/{test_bucket.id}",
        json={
            "name": "Updated Vacation",
            "target_amount": 1500.0,
            "current_saved_amount": 500.0,
            "priority_score": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Vacation"
    assert data["target_amount"] == 1500.0
    assert data["current_saved_amount"] == 500.0
    assert data["id"] == test_bucket.id

def test_update_nonexistent_bucket(client):
    """Test updating a bucket that doesn't exist."""
    response = client.put(
        "/buckets/999",
        json={
            "name": "Nonexistent Bucket"
        }
    )
    assert response.status_code == 404
    assert "Bucket not found" in response.json()["detail"]

def test_delete_bucket(client, test_bucket):
    """Test deleting a bucket."""
    response = client.delete(f"/buckets/{test_bucket.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_bucket.id
    
    # Verify the bucket was deleted
    response = client.get(f"/buckets/{test_bucket.id}")
    assert response.status_code == 404

def test_delete_nonexistent_bucket(client):
    """Test deleting a bucket that doesn't exist."""
    response = client.delete("/buckets/999")
    assert response.status_code == 404
    assert "Bucket not found" in response.json()["detail"]
