from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Database URL is loaded from .env by Pydantic BaseSettings in config.py
# (env_file=".env" — no need for extra load_dotenv() here)

# Pool configuration for connection management - Optimized for production
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    pool_size=settings.DB_POOL_SIZE,  # Increased to 20 for concurrency
    max_overflow=settings.DB_MAX_OVERFLOW,  # Increased to 40
    pool_timeout=settings.DB_POOL_TIMEOUT,  # 30 seconds timeout
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle after 1 hour
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Note: Models are imported in app.main after Base is defined
# This prevents circular import issues

# Dependency injection for database sessions
def get_db():
    """Database session dependency
    Usage: def my_endpoint(db: Session = Depends(get_db)).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
