from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from .api.routes import (
    auth_router, user_routes, transaction_routes,
    bucket_routes, expenses_routes, income_routes, 
    financial_summary_routes
)
import uvicorn
import logging
import os
from dotenv import load_dotenv
from .database import engine, Base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import redis
from .core.redis_manager import get_redis_connection
from semantic_kernel import Kernel 
from app.rootdialog import BucketPlugin
from pydantic import BaseModel



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ChatRequest(BaseModel):
    user_input: str


# Lifespan context manager (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created or verified")
        
        # Test Redis connection on startup
        try:
            r = get_redis_connection()
            r.ping()
            logger.info("Redis connection established successfully")
        except redis.RedisError as e:
            logger.error(f"Redis connection error: {e}")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {e}")
    except Exception as e:
        logger.error(f"Startup error: {e}")
    
    yield  # This is where FastAPI runs
    
    # Shutdown logic
    logger.info("Application shutting down")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# Create the Semantic Kernel
kernel = Kernel()

# Create a simple endpoint to interact with the chatbot
async def chat(user_input: str):
    # Simulate chatbot processing (replace with actual chatbot logic)
    return f"Chatbot response to: {user_input}"

@app.post("/invoke-chatbot")
async def invoke_chatbot(request: ChatRequest):
    return {"response": f"You said: {request.message}"}

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_routes, prefix="/users", tags=["users"])
app.include_router(transaction_routes, prefix="/transactions", tags=["transactions"])
app.include_router(bucket_routes, prefix="/buckets", tags=["buckets"])
app.include_router(expenses_routes, prefix="/expenses", tags=["expenses"])
app.include_router(income_routes, prefix="/incomes", tags=["incomes"])
app.include_router(financial_summary_routes, prefix="/financial-summaries", tags=["financial-summaries"])

@app.get("/")
async def root():
    return {"message": "Im healthy 😎"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
