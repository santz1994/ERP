"""
Application Configuration
Centralized settings for development, testing, and production
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseSettings, Field


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Environment
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT)
    DEBUG: bool = Field(default=True)
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:password@localhost:5432/erp_quty_karunia")
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)
    DATABASE_POOL_PRE_PING: bool = Field(default=True)
    
    # JWT/Security
    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=7)
    
    # API
    API_TITLE: str = Field(default="ERP Quty Karunia")
    API_VERSION: str = Field(default="2.0.0")
    API_DESCRIPTION: str = Field(default="Manufacturing Execution System - IKEA Standard")
    API_PREFIX: str = Field(default="/api/v1")
    
    # CORS
    CORS_ORIGINS: list = Field(default=["http://localhost:3000", "http://localhost:8080"])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: list = Field(default=["*"])
    CORS_ALLOW_HEADERS: list = Field(default=["*"])
    
    # Timezone
    TIMEZONE: str = Field(default="Asia/Jakarta")  # WIB (Indonesia)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")  # 'json' for structured logging, 'text' for human-readable
    
    # Features
    ENABLE_TRACING: bool = Field(default=False)
    ENABLE_METRICS: bool = Field(default=True)
    ENABLE_TRAINING_MODE: bool = Field(default=False)  # Simulation mode for training
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True)
    PROMETHEUS_PORT: int = Field(default=8001)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings


# Validation
if settings.ENVIRONMENT == Environment.PRODUCTION:
    assert settings.JWT_SECRET_KEY != "your-secret-key-change-in-production", \
        "JWT_SECRET_KEY must be changed in production!"
    assert settings.DEBUG is False, "DEBUG must be False in production!"
