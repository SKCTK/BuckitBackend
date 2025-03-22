import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import base64
import hashlib
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
import json
from datetime import datetime, UTC

# Import the router to test
from app.api.routes.auth import router

# Create a test FastAPI app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture
def mock_env_variables():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        "SECRET_KEY": "test-secret-key",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30"
    }):
        yield

@pytest.fixture
def mock_redis():
    """Mock Redis functionality for testing"""
    # Create an in-memory store for test data
    test_data_store = {}
    
    # Mock Redis connection and functions
    with patch('app.api.routes.auth.store_auth_code') as mock_store, \
         patch('app.api.routes.auth.safely_use_and_delete_auth_code') as mock_use_delete:
        
        # Set up the store_auth_code mock
        def store_side_effect(auth_code, data, expiry_minutes=10):
            test_data_store[f"auth:{auth_code}"] = json.dumps(data)
            return True
            
        mock_store.side_effect = store_side_effect
        
        # Set up the safely_use_and_delete_auth_code mock
        def use_delete_side_effect(auth_code):
            key = f"auth:{auth_code}"
            if key in test_data_store:
                data = json.loads(test_data_store[key])
                del test_data_store[key]
                return data
            return None
            
        mock_use_delete.side_effect = use_delete_side_effect
        
        yield test_data_store

def test_authorize_endpoint(mock_redis):
    """Test the authorize endpoint creates and returns an auth code"""
    response = client.post(
        "/authorize",
        data={
            "client_id": "test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "code_challenge": "test-challenge"
        }
    )
    
    assert response.status_code == 200
    assert "auth_code" in response.json()
    
    # Verify the auth code was stored in our mock Redis
    auth_code = response.json()["auth_code"]
    key = f"auth:{auth_code}"
    assert key in mock_redis
    
    stored_data = json.loads(mock_redis[key])
    assert stored_data["code_challenge"] == "test-challenge"
    assert stored_data["client_id"] == "test-client"
    assert stored_data["redirect_uri"] == "http://localhost:3000/callback"

def test_token_endpoint_success(mock_redis):
    """Test successful token exchange with valid code verifier"""
    # First create an auth code
    code_verifier = "test-verifier"
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    
    auth_code = "test-auth-code"
    
    # Store in our mock Redis
    mock_redis[f"auth:{auth_code}"] = json.dumps({
        "client_id": "test-client",
        "redirect_uri": "http://localhost:3000/callback",
        "code_challenge": code_challenge,
        "created_at": datetime.now(UTC).isoformat()
    })
    
    # Now exchange it for a token
    with patch('app.api.routes.auth.jwt.encode', return_value="test-access-token"):
        response = client.post(
            "/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "code_verifier": code_verifier
            }
        )
    
    assert response.status_code == 200
    token_data = response.json()
    assert token_data["access_token"] == "test-access-token"
    assert token_data["token_type"] == "bearer"
    
    # Verify the auth code was consumed (deleted from Redis)
    assert f"auth:{auth_code}" not in mock_redis

def test_token_endpoint_invalid_grant_type():
    """Test error handling for invalid grant type"""
    response = client.post(
        "/token",
        data={
            "grant_type": "invalid",
            "code": "test-code",
            "code_verifier": "test-verifier"
        }
    )
    
    assert response.status_code == 400
    assert "Unsupported grant type" in response.json()["detail"]

def test_token_endpoint_invalid_code(mock_redis):
    """Test error handling for invalid auth code"""
    response = client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "code": "invalid-code",
            "code_verifier": "test-verifier"
        }
    )
    
    assert response.status_code == 400
    assert "Invalid or expired code" in response.json()["detail"]

def test_token_endpoint_invalid_verifier(mock_redis):
    """Test error handling for invalid code verifier"""
    # Create an auth code with a specific challenge
    auth_code = "test-auth-code"
    
    # Store in our mock Redis with a known challenge
    mock_redis[f"auth:{auth_code}"] = json.dumps({
        "client_id": "test-client",
        "redirect_uri": "http://localhost:3000/callback",
        "code_challenge": "correct-challenge",
        "created_at": datetime.now(UTC).isoformat()
    })
    
    response = client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "code_verifier": "wrong-verifier"  # This will generate a different challenge
        }
    )
    
    assert response.status_code == 400
    assert "Invalid code verifier" in response.json()["detail"]
