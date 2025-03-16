import pytest
from app.model import schemas

def test_create_user(client):
    """Test creating a user."""
    response = client.post(
        "/users/users/",
        json={
            "name": "New User",
            "email": "new@example.com",
            "password": "newpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New User"
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_create_user_duplicate_email(client, test_user):
    """Test creating a user with an email that already exists."""
    response = client.post(
        "/users/users/",
        json={
            "name": "Another User",
            "email": "test@example.com",  # Same email as test_user
            "password": "password456"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_get_user(client, test_user):
    """Test getting a user by ID."""
    response = client.get(f"/users/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_user.name
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

def test_get_nonexistent_user(client):
    """Test getting a user that doesn't exist."""
    response = client.get("/users/users/999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_update_user(client, test_user):
    """Test updating a user."""
    response = client.put(
        f"/users/users/{test_user.id}",
        json={
            "name": "Updated Name",
            "email": "updated@example.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "updated@example.com"
    assert data["id"] == test_user.id

def test_update_nonexistent_user(client):
    """Test updating a user that doesn't exist."""
    response = client.put(
        "/users/users/999",
        json={
            "name": "New Name"
        }
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_delete_user(client, test_user):
    """Test deleting a user."""
    response = client.delete(f"/users/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    
    # Verify the user was deleted
    response = client.get(f"/users/users/{test_user.id}")
    assert response.status_code == 404

def test_delete_nonexistent_user(client):
    """Test deleting a user that doesn't exist."""
    response = client.delete("/users/users/999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]
