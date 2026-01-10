from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.database import engine, Base
from app.routes import users
from app.events import event_publisher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
    
    # Connect to RabbitMQ
    try:
        event_publisher.connect()
        logger.info("RabbitMQ connection established")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
    
    logger.info(f"{settings.SERVICE_NAME} started successfully")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")
    event_publisher.close()
    logger.info(f"{settings.SERVICE_NAME} shut down successfully")

# Create FastAPI app
app = FastAPI(
    title="UCE User Service",
    description="Microservicio de gestión de perfiles de usuario",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        content={"detail": "Error interno del servidor"}
    )

# Include routers
app.include_router(users.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
