"""
Application Configuration
Centralized settings for development, testing, and production
"""

import os
import json
from enum import Enum
from typing import Optional, Union, List
from pydantic import BaseSettings, Field, validator


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
    DB_POOL_SIZE: int = Field(default=20)  # Increased from 5 for better concurrency
    DB_MAX_OVERFLOW: int = Field(default=40)  # Increased from 10
    DB_POOL_TIMEOUT: int = Field(default=30)  # Connection timeout in seconds
    DB_POOL_RECYCLE: int = Field(default=3600)  # Recycle connections after 1 hour
    DATABASE_POOL_PRE_PING: bool = Field(default=True)
    
    # JWT/Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")  # Current active key
    SECRET_KEYS_HISTORY: str = Field(default="")  # Comma-separated list of previous keys
    KEY_LAST_ROTATED: Optional[str] = Field(default=None)  # ISO timestamp of last rotation
    KEY_ROTATION_DAYS: int = Field(default=90)  # Rotate every 90 days
    
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24)
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=7)
    
    @property
    def all_valid_keys(self) -> list:
        """Return current key + historical keys for JWT validation"""
        keys = [self.SECRET_KEY]
        if self.SECRET_KEYS_HISTORY:
            historical_keys = [k.strip() for k in self.SECRET_KEYS_HISTORY.split(",") if k.strip()]
            keys.extend(historical_keys)
        return keys
    
    # API
    API_TITLE: str = Field(default="ERP Quty Karunia")
    API_VERSION: str = Field(default="2.0.0")
    API_DESCRIPTION: str = Field(default="Manufacturing Execution System - IKEA Standard")
    API_PREFIX: str = Field(default="/api/v1")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(default=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:5173",  # Vite default dev port
        "http://localhost:8080"
    ])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: list = Field(default=["*"])
    CORS_ALLOW_HEADERS: list = Field(default=["*"])
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list"""
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                # Fall back to comma-separated parsing
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        else:
            return ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]
    
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
