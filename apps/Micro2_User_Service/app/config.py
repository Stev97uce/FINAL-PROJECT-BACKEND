from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "user_service_db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    REDIS_PASSWORD: str = ""
    
    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Service
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8001
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def DATABASE_URL(self) -> str:
        # URL-encode password and user to handle special characters
        encoded_password = quote_plus(self.DB_PASSWORD)
        encoded_user = quote_plus(self.DB_USER)
        return f"postgresql://{encoded_user}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str:
        # URL-encode Redis password if provided
        if self.REDIS_PASSWORD:
            encoded_password = quote_plus(self.REDIS_PASSWORD)
            return f"redis://:{encoded_password}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar variables extra del .env que no estén definidas

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
