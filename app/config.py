"""Application configuration and environment setup"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./hospital.db"
    )
    
    # Application Settings
    APP_NAME: str = "Hospital Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Connection Pool
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
