"""
FastAPI application - Notification Service
KISS principle: Simple FastAPI app with lifespan events
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Database
from app.consumer import rabbitmq_consumer
from app.services.mqtt_service import mqtt_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}")
    
    # Connect to MongoDB
    await Database.connect_db()
    
    # Start RabbitMQ consumer
    rabbitmq_consumer.start()
    
    # MQTT is initialized on import
    logger.info("All services initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down services")
    
    # Stop RabbitMQ consumer
    rabbitmq_consumer.stop()
    
    # Disconnect MQTT
    mqtt_service.disconnect()
    
    # Close MongoDB
    await Database.close_db()
    
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Multi-channel notification delivery (Email, WhatsApp, Internal, MQTT)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.routes import health, notifications, preferences, admin

app.include_router(health.router)
app.include_router(notifications.router)
app.include_router(preferences.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running"
    }
