from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from .config import settings

# Database URL (usando psycopg en lugar de psycopg2)
# URL-encode password and user to handle special characters
encoded_password = quote_plus(settings.DB_PASSWORD)
encoded_user = quote_plus(settings.DB_USER)
DATABASE_URL = f"postgresql+psycopg://{encoded_user}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Engine
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
