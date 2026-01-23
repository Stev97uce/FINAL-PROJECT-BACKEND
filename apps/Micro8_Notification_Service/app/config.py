"""
Configuration settings for Notification Service
KISS principle: Simple, environment-based configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8007
    DEBUG: bool = True
    
    # MongoDB
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB_NAME: str = "notification_db"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_EXCHANGE: str = "uce_events"
    
    # MQTT
    MQTT_BROKER_HOST: str = "mqtt"
    MQTT_BROKER_PORT: int = 1883
    MQTT_CLIENT_ID: str = "notification-service"
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    # SendGrid (Email)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@uce.edu.ec"
    SENDGRID_FROM_NAME: str = "UCE Psychology System"
    
    # Twilio (WhatsApp)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = ""  # Format: whatsapp:+1234567890
    
    # Auth Service Integration
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_EMAIL_PER_USER_DAY: int = 100
    RATE_LIMIT_EMAIL_GLOBAL_HOUR: int = 1000
    RATE_LIMIT_WHATSAPP_PER_USER_DAY: int = 50
    RATE_LIMIT_INTERNAL_PER_USER_DAY: int = 200
    
    # Retry Configuration
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAYS: list = [300, 1800, 7200]  # 5min, 30min, 2h in seconds
    
    # Notification Expiry
    INTERNAL_NOTIFICATION_EXPIRY_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
