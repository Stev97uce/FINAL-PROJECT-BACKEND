from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import engine, Base
from .events import rabbitmq_publisher
from .routes import patients, expedientes

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja eventos de inicio y cierre de la aplicación"""
    # Startup
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    # Crear tablas
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas de base de datos verificadas/creadas")
    except Exception as e:
        logger.error(f"Error creando tablas: {e}")
    
    # Conectar a RabbitMQ
    try:
        rabbitmq_publisher.connect()
    except Exception as e:
        logger.warning(f"No se pudo conectar a RabbitMQ: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando conexiones...")
    try:
        rabbitmq_publisher.close()
    except Exception as e:
        logger.error(f"Error cerrando RabbitMQ: {e}")
    
    logger.info("Aplicación cerrada")

# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Microservicio para gestión de consultantes/pacientes y expedientes clínicos",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc) if settings.DEBUG else "Ha ocurrido un error inesperado"
        }
    )

# Incluir routers
app.include_router(patients.router)
app.include_router(expedientes.router)

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
