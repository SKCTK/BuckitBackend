from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
import hashlib
import base64
import uuid
from datetime import datetime, timedelta, UTC  # Added UTC import
from jose import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# In-memory store for demo purposes.
# In production, use a persistent storage solution.
oauth_store = {}

# Load secrets and config from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/authorize")
async def authorize(
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    code_challenge: str = Form(...),
):
    # Validate client_id and redirect_uri as needed.
    # Generate a unique authorization code.
    auth_code = str(uuid.uuid4())
    # Store client details along with the code_challenge.
    oauth_store[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge
    }
    return {"auth_code": auth_code}

@router.post("/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    code_verifier: str = Form(...),
) -> Token:
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Unsupported grant type")
    
    stored = oauth_store.get(code)
    if not stored:
        raise HTTPException(status_code=400, detail="Invalid authorization code")
    
    def compute_code_challenge(verifier: str) -> str:
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    expected_challenge = stored["code_challenge"]
    computed_challenge = compute_code_challenge(code_verifier)
    if computed_challenge != expected_challenge:
        raise HTTPException(status_code=400, detail="Invalid code verifier")
    
    # Generate the JWT access token.
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Updated to use datetime.now(UTC)
    token_payload = {
        "sub": stored["client_id"],
        "exp": expire
    }
    access_token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    # Clean up stored auth code (one-time use)
    del oauth_store[code]

    return Token(access_token=access_token, token_type="bearer")
