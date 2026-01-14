"""
MongoDB database connection using Motor and Beanie ODM
KISS principle: Simple async connection
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            
            # Import models here to avoid circular imports
            from app.models import (
                NotificationTemplate,
                NotificationLog,
                UserPreferences,
                InternalNotification
            )
            
            # Initialize Beanie with models
            await init_beanie(
                database=cls.client[settings.MONGODB_DB_NAME],
                document_models=[
                    NotificationTemplate,
                    NotificationLog,
                    UserPreferences,
                    InternalNotification
                ]
            )
            
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")


# Redis connection (simple sync for rate limiting)
import redis

def get_redis_client():
    """Get Redis client for rate limiting and caching"""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
