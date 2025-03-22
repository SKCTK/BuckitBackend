import pytest
from unittest.mock import patch, MagicMock
import json
import redis
from app.core.redis_manager import (
    get_redis_connection,
    store_auth_code,
    get_auth_code_data,
    delete_auth_code,
    safely_use_and_delete_auth_code
)

def test_store_auth_code(mock_redis_service):
    """Test storing an auth code in Redis."""
    # Arrange
    auth_code = "test-auth-code"
    data = {"client_id": "test-client", "code_challenge": "test-challenge"}
    
    # Act
    result = store_auth_code(auth_code, data)
    
    # Assert
    assert result is True
    assert f"auth:{auth_code}" in mock_redis_service
    stored_data = json.loads(mock_redis_service[f"auth:{auth_code}"])
    assert stored_data == data

def test_get_auth_code_data(mock_redis_service):
    """Test retrieving auth code data from Redis."""
    # Arrange
    auth_code = "test-auth-code"
    data = {"client_id": "test-client", "code_challenge": "test-challenge"}
    mock_redis_service[f"auth:{auth_code}"] = json.dumps(data)
    
    # Act
    result = get_auth_code_data(auth_code)
    
    # Assert
    assert result == data

def test_get_nonexistent_auth_code_data(mock_redis_service):
    """Test retrieving non-existent auth code data from Redis."""
    # Act
    result = get_auth_code_data("nonexistent-code")
    
    # Assert
    assert result is None

def test_delete_auth_code(mock_redis_service):
    """Test deleting an auth code from Redis."""
    # Arrange
    auth_code = "test-auth-code"
    data = {"client_id": "test-client", "code_challenge": "test-challenge"}
    mock_redis_service[f"auth:{auth_code}"] = json.dumps(data)
    
    # Act
    result = delete_auth_code(auth_code)
    
    # Assert
    assert result == 1
    assert f"auth:{auth_code}" not in mock_redis_service

def test_delete_nonexistent_auth_code(mock_redis_service):
    """Test deleting a non-existent auth code from Redis."""
    # Act
    result = delete_auth_code("nonexistent-code")
    
    # Assert
    assert result == 0

def test_safely_use_and_delete_auth_code(mock_redis_service):
    """Test atomically retrieving and deleting an auth code from Redis."""
    # Arrange
    auth_code = "test-auth-code"
    data = {"client_id": "test-client", "code_challenge": "test-challenge"}
    mock_redis_service[f"auth:{auth_code}"] = json.dumps(data)
    
    # Act
    result = safely_use_and_delete_auth_code(auth_code)
    
    # Assert
    assert result == data
    assert f"auth:{auth_code}" not in mock_redis_service

def test_safely_use_and_delete_nonexistent_auth_code(mock_redis_service):
    """Test atomically retrieving and deleting a non-existent auth code from Redis."""
    # Act
    result = safely_use_and_delete_auth_code("nonexistent-code")
    
    # Assert
    assert result is None

def test_redis_connection_error():
    """Test handling Redis connection errors."""
    # Arrange
    with patch('app.core.redis_manager.get_redis_connection', side_effect=redis.RedisError("Connection error")):
        # Act & Assert
        assert store_auth_code("code", {}) is False
        assert get_auth_code_data("code") is None
        assert delete_auth_code("code") == 0
        assert safely_use_and_delete_auth_code("code") is None
