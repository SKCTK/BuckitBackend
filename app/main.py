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

# Correct Semantic Kernel imports
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    AzureRealtimeWebsocket,
    AzureRealtimeExecutionSettings,
    ListenEvents,
    TurnDetection
)
from semantic_kernel.contents import ChatHistory, RealtimeTextEvent

# Import the BucketPlugin
from .plugins.bucket_plugin import BucketPlugin

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
active_agents: Dict[int, AzureRealtimeWebsocket] = {}

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
            
        # Check for Azure OpenAI credentials
        if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
            logger.info("Azure OpenAI credentials found for chat functionality")
        else:
            logger.warning("AZURE_OPENAI_API_KEY and/or AZURE_OPENAI_ENDPOINT not set - chat functionality will be limited")
            
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
    
    # Register the BucketPlugin using the exact format from documentation
    bucket_plugin = BucketPlugin()
    kernel.add_plugin(bucket_plugin, plugin_name="budget")
    
    logger.info("Bucket Plugin registered with Semantic Kernel")
    return kernel

# Direct WebSocket endpoint in main.py
# Update the WebSocket endpoint:

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    logger.info(f"WebSocket connection established for user {user_id}")
    
    try:
        # Use the exact values that worked in your test
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        
        if not api_key or not endpoint:
            raise ValueError("Azure OpenAI credentials not found")
        
        # Setup kernel with our plugins
        kernel = await setup_kernel()
        
        # Configure Azure OpenAI service with function calling
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
        from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
        from semantic_kernel.functions.kernel_arguments import KernelArguments
        
        service_id = "azure-chat"
        azure_chat_service = AzureChatCompletion(
            service_id=service_id,
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        # Add the service to the kernel
        kernel.add_service(azure_chat_service)
        
        logger.info(f"Azure OpenAI service created for user {user_id} with deployment {deployment} and function calling enabled")
        
        # Create a chat history
        chat_history = ChatHistory()
        chat_history.add_system_message("""
        You are a financial advisor assistant helping users with:
        - Budgeting advice
        - Investment recommendations
        - Financial planning
        
        Be clear, concise and helpful. When you don't know something,
        be transparent about it. Don't fabricate financial information.
        """)
        
        # Chat loop
        while True:
            # Get message from WebSocket
            data = await websocket.receive_text()
            message = json.loads(data)
            message_text = message.get("text", "")
            
            if not message_text.strip():
                continue
            
            logger.info(f"Message from user {user_id}: {message_text}")
            
            # Add user message to chat history
            chat_history.add_user_message(message_text)
            
            try:
                # Show typing indicator to user
                await websocket.send_text(json.dumps({
                    "text": "...",
                    "sender": "typing",
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Create execution settings with function choice behavior
                execution_settings = PromptExecutionSettings(
                    function_choice_behavior=FunctionChoiceBehavior.Auto()
                )
                
                # Create kernel arguments with the settings
                arguments = KernelArguments(
                    settings=execution_settings
                )
                
                # Get chat service directly
                chat_service = kernel.get_service(service_id)
                
                # Use get_chat_message_content instead of invoke_prompt
                response = await chat_service.get_chat_message_content(
                    chat_history=chat_history,
                    settings=execution_settings,
                    kernel=kernel
                )
                
                # Get the response content - response is a ChatMessageContent object
                result_text = response.content if hasattr(response, "content") else str(response)
                
                # Add the assistant's response to chat history
                chat_history.add_assistant_message(result_text)
                
                # Send response back to user
                await websocket.send_text(json.dumps({
                    "text": result_text,
                    "sender": "bot",
                    "timestamp": datetime.now().isoformat()
                }))
                
            except Exception as e:
                logger.error(f"Azure OpenAI API error: {str(e)}", exc_info=True)
                await websocket.send_text(json.dumps({
                    "text": f"Sorry, I encountered an error: {str(e)}",
                    "sender": "system",
                    "timestamp": datetime.now().isoformat()
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for user {user_id}")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        try:
            await websocket.send_text(json.dumps({
                "text": f"Configuration error: {str(e)}",
                "sender": "system",
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass
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