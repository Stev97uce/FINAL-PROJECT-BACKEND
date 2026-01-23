from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import (
    connect_to_mongo,
    close_mongo_connection,
    connect_to_redis,
    close_redis_connection
)
from app.events import rabbitmq_publisher
from app.routes import clinical_records, sessions, session_notes, therapeutic_goals

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    await connect_to_mongo()
    connect_to_redis()
    rabbitmq_publisher.connect()
    logger.info(f"Service running on port {settings.PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down service")
    await close_mongo_connection()
    close_redis_connection()
    rabbitmq_publisher.close()
    logger.info("Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Clinical Service API",
    description="Microservicio de Gestión Clínica - UCE Mental Health Platform",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clinical_records.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(session_notes.router, prefix="/api/v1")
app.include_router(therapeutic_goals.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
