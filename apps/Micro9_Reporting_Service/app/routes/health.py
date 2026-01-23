"""
Health check endpoint
KISS principle: Simple health verification
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from app.schemas import HealthCheck
from app.database import get_db, get_redis
import pika

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Check service health
    """
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    # Check Redis
    try:
        redis = get_redis()
        redis.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"
    
    # Check RabbitMQ (simplified)
    rabbitmq_status = "unknown"
    
    return HealthCheck(
        status="healthy" if db_status == "connected" else "unhealthy",
        service="reporting-service",
        database=db_status,
        redis=redis_status,
        rabbitmq=rabbitmq_status,
        timestamp=datetime.utcnow()
    )


@router.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": "reporting-service",
        "version": "1.0.0",
        "status": "running"
    }
