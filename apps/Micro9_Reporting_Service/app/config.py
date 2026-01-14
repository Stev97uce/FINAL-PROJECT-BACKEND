"""
Configuration settings for Reporting Service
KISS principle: Simple, clear configuration
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Reporting Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8008"))
    
    # Database (PostgreSQL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/reporting_db"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))
    
    # RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST: str = os.getenv("RABBITMQ_VHOST", "/")
    RABBITMQ_EXCHANGE: str = "uce_events"
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = os.getenv("CELERY_TIMEZONE", "America/Guayaquil")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "Q7v1P7Rp-vglhy04pduFZ0LeHW-_z9eBqSPwEV_2Ea4")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    CORS_METHODS: str = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS")
    CORS_HEADERS: str = os.getenv("CORS_HEADERS", "*")
    
    # Microservices URLs
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
    PATIENT_SERVICE_URL: str = os.getenv("PATIENT_SERVICE_URL", "http://localhost:8002")
    APPOINTMENT_SERVICE_URL: str = os.getenv("APPOINTMENT_SERVICE_URL", "http://localhost:8003")
    ROOM_SERVICE_URL: str = os.getenv("ROOM_SERVICE_URL", "http://localhost:8004")
    CLINICAL_SERVICE_URL: str = os.getenv("CLINICAL_SERVICE_URL", "http://localhost:8005")
    SUPERVISION_SERVICE_URL: str = os.getenv("SUPERVISION_SERVICE_URL", "http://localhost:8006")
    NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8007")
    
    # Report Generation
    REPORTS_STORAGE_PATH: str = os.getenv("REPORTS_STORAGE_PATH", "/tmp/reports")
    REPORTS_MAX_FILE_SIZE_MB: int = int(os.getenv("REPORTS_MAX_FILE_SIZE_MB", "50"))
    REPORTS_RETENTION_DAYS: int = int(os.getenv("REPORTS_RETENTION_DAYS", "90"))
    DEFAULT_REPORT_FORMAT: str = os.getenv("DEFAULT_REPORT_FORMAT", "pdf")
    ENABLE_CHARTS: bool = os.getenv("ENABLE_CHARTS", "True").lower() == "true"
    
    # Scheduled Reports
    ENABLE_SCHEDULED_REPORTS: bool = os.getenv("ENABLE_SCHEDULED_REPORTS", "True").lower() == "true"
    SCHEDULER_TIMEZONE: str = os.getenv("SCHEDULER_TIMEZONE", "America/Guayaquil")
    
    # Limits
    MAX_CONCURRENT_REPORTS: int = int(os.getenv("MAX_CONCURRENT_REPORTS", "5"))
    REPORT_TIMEOUT_SECONDS: int = int(os.getenv("REPORT_TIMEOUT_SECONDS", "300"))
    MAX_DATA_ROWS_PER_REPORT: int = int(os.getenv("MAX_DATA_ROWS_PER_REPORT", "10000"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    @property
    def redis_url(self) -> str:
        """Build Redis URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def rabbitmq_url(self) -> str:
        """Build RabbitMQ URL"""
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
