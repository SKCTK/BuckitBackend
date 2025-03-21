from fastapi import FastAPI, Depends
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Lifespan context manager (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created or verified")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {e}")
    except Exception as e:
        logger.error(f"Startup error: {e}")
    
    yield  # This is where FastAPI runs
    
    # Shutdown logic
    logger.info("Application shutting down")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

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
