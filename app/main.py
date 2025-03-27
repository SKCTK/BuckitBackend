from fastapi import FastAPI, Depends, Request, status, WebSocket, WebSocketDisconnect
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
import json
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
from .database import engine, Base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import redis
from .core.redis_manager import get_redis_connection

# Import Semantic Kernel components for the AI chat
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIRealtimeWebsocket,
    OpenAIRealtimeExecutionSettings,
    RealtimeTextEvent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Store active connections
active_connections: Dict[int, WebSocket] = {}
active_agents: Dict[int, OpenAIRealtimeWebsocket] = {}

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
            
        # Check for OpenAI API key
        if os.getenv("OPENAI_API_KEY"):
            logger.info("OpenAI API key found for chat functionality")
        else:
            logger.warning("OPENAI_API_KEY not set - chat functionality will be limited")
            
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

# Simple kernel setup function
async def setup_kernel() -> Kernel:
    """Create and configure a Semantic Kernel for the chat."""
    kernel = Kernel()
    # You can add plugins here later if needed
    return kernel

# Direct WebSocket endpoint in main.py
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    logger.info(f"WebSocket connection established for user {user_id}")
    
    try:
        kernel = await setup_kernel()
        
        # Configure agent with simple financial advice capabilities
        agent = OpenAIRealtimeWebsocket()
        settings = OpenAIRealtimeExecutionSettings(
            model="gpt-4o",
            instructions="""
            You are a financial advisor assistant helping users with:
            - Budgeting advice
            - Investment recommendations
            - Financial planning
            
            Be clear, concise and helpful. When you don't know something,
            be transparent about it. Don't fabricate financial information.
            """,
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        active_agents[user_id] = agent
        
        # Start the agent session
        async with agent(
            settings=settings,
            kernel=kernel,
            create_response=True,
        ):
            # Handle incoming messages from user
            receive_task = None
            
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                message_text = message.get("text", "")
                
                if not message_text.strip():
                    continue
                
                logger.info(f"Message from user {user_id}: {message_text}")
                
                # Send the message to the agent
                await agent.send(RealtimeTextEvent(text=message_text))
                
                # Process responses from the agent
                async for event in agent.receive():
                    if isinstance(event, RealtimeTextEvent) and event.text:
                        await websocket.send_text(json.dumps({
                            "text": event.text,
                            "sender": "bot",
                            "timestamp": datetime.now().isoformat()
                        }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for user {user_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket: {str(e)}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                "text": f"An error occurred: {str(e)}",
                "sender": "system",
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass
    finally:
        if user_id in active_connections:
            del active_connections[user_id]
        if user_id in active_agents:
            del active_agents[user_id]

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