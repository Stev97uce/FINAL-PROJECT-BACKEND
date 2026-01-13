from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from redis import Redis
import logging
from app.config import settings
from app.models import ClinicalRecord, Session, SessionNote, TherapeuticGoal

logger = logging.getLogger(__name__)

# MongoDB client
mongodb_client: AsyncIOMotorClient = None

# Redis client
redis_client: Redis = None


async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie"""
    global mongodb_client
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        await init_beanie(
            database=mongodb_client[settings.MONGODB_DB_NAME],
            document_models=[
                ClinicalRecord,
                Session,
                SessionNote,
                TherapeuticGoal
            ]
        )
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


def connect_to_redis():
    """Connect to Redis"""
    global redis_client
    try:
        redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
        redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        raise


def close_redis_connection():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")


def get_redis() -> Redis:
    """Get Redis client instance"""
    return redis_client
