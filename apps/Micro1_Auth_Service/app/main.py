from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base
from app.routes import auth
from app.events import event_publisher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Auth Service...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Connect to RabbitMQ
    try:
        event_publisher.connect()
        logger.info("RabbitMQ connection established")
    except Exception as e:
        logger.error(f"Error connecting to RabbitMQ: {e}")
    
    logger.info("Auth Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Auth Service...")
    event_publisher.close()
    logger.info("Auth Service stopped")


# Create FastAPI app
app = FastAPI(
    title="UCE Auth Service",
    description="Microservicio de autenticación para el sistema de gestión de consultantes UCE",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


# Include routers
app.include_router(auth.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "UCE Auth Service",
        "version": "1.0.0",
        "status": "running"
    }
