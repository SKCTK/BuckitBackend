import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import base64
import hashlib
import os
from unittest.mock import patch
from dotenv import load_dotenv

# Import the router to test
from app.api.routes.auth import router, oauth_store

# Create a test FastAPI app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture
def mock_env_variables():
    """Mock environment variables for testing"""
    # Load values from .env.test in __tests__ directory
    env_path = Path(__file__).parent / ".env.test"
    load_dotenv(env_path)
    
    # Use the loaded values or fallback to defaults
    with patch.dict(os.environ, {
        "SECRET_KEY": os.getenv("SECRET_KEY", "test-secret-key"),
        "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    }):
        yield

def test_authorize_endpoint():
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
    
    # Verify the auth code is stored with the challenge
    auth_code = response.json()["auth_code"]
    assert auth_code in oauth_store
    assert oauth_store[auth_code]["code_challenge"] == "test-challenge"
    assert oauth_store[auth_code]["client_id"] == "test-client"
    assert oauth_store[auth_code]["redirect_uri"] == "http://localhost:3000/callback"

def test_token_endpoint_success():
    """Test successful token exchange with valid code verifier"""
    # First create an auth code
    code_verifier = "test-verifier"
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    
    auth_code = "test-auth-code"
    oauth_store[auth_code] = {
        "client_id": "test-client",
        "redirect_uri": "http://localhost:3000/callback",
        "code_challenge": code_challenge
    }
    
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
    
    # Verify the auth code was consumed (deleted)
    assert auth_code not in oauth_store

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

def test_token_endpoint_invalid_code():
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
    assert "Invalid authorization code" in response.json()["detail"]

def test_token_endpoint_invalid_verifier():
    """Test error handling for invalid code verifier"""
    # Create an auth code with a specific challenge
    auth_code = "test-auth-code"
    oauth_store[auth_code] = {
        "client_id": "test-client",
        "redirect_uri": "http://localhost:3000/callback",
        "code_challenge": "correct-challenge"
    }
    
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
