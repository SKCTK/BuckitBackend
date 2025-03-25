import redis
import os
import json
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Configure connection pool for concurrent access
redis_pool = redis.ConnectionPool(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    max_connections=100  # Important for high concurrency
)

# Get connection from pool
def get_redis_connection():
    """Get a connection from the Redis connection pool."""
    return redis.Redis(connection_pool=redis_pool)

def store_auth_code(auth_code, data, expiry_minutes=10):
    """
    Store authorization code with expiration.
    
    Args:
        auth_code (str): The authorization code
        data (dict): Data to store with the auth code
        expiry_minutes (int): Expiration time in minutes
    
    Returns:
        bool: True if storage was successful
    """
    try:
        r = get_redis_connection()
        return r.setex(
            f"auth:{auth_code}", 
            timedelta(minutes=expiry_minutes),
            json.dumps(data)
        )
    except redis.RedisError as e:
        logger.error(f"Redis error storing auth code: {e}")
        return False

def get_auth_code_data(auth_code):
    """
    Retrieve data associated with an authorization code.
    
    Args:
        auth_code (str): The authorization code
    
    Returns:
        dict or None: The data if found, None if not found or error
    """
    try:
        r = get_redis_connection()
        data = r.get(f"auth:{auth_code}")
        if not data:
            return None
        return json.loads(data)
    except redis.RedisError as e:
        logger.error(f"Redis error retrieving auth code: {e}")
        return None

def delete_auth_code(auth_code):
    """
    Delete an authorization code.
    
    Args:
        auth_code (str): The authorization code
    
    Returns:
        int: Number of keys deleted (0 or 1)
    """
    try:
        r = get_redis_connection()
        return r.delete(f"auth:{auth_code}")
    except redis.RedisError as e:
        logger.error(f"Redis error deleting auth code: {e}")
        return 0

def safely_use_and_delete_auth_code(auth_code):
    """
    Atomically retrieve and delete an auth code to prevent race conditions.
    
    Args:
        auth_code (str): The authorization code
    
    Returns:
        dict or None: The data if found, None if not found, already used, or error
    """
    try:
        r = get_redis_connection()
        pipe = r.pipeline()
        pipe.get(f"auth:{auth_code}")
        pipe.delete(f"auth:{auth_code}")
        results = pipe.execute()
        
        # If no data was found (code doesn't exist or was already used)
        if not results[0]:
            return None
        
        # Return the data
        return json.loads(results[0])
    except redis.RedisError as e:
        logger.error(f"Redis error in safely_use_and_delete_auth_code: {e}")
        return None
