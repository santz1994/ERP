from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/erp_quty_karunia"
)

# Pool configuration for connection management
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import all models to register them with Base
# This ensures tables are created when Base.metadata.create_all() is called
from app.core.models import (
    User,
    Product, Category,
    BOMHeader, BOMDetail,
    ManufacturingOrder, WorkOrder, MaterialConsumption,
    TransferLog, LineOccupancy,
    Location, StockMove, StockQuant,
    QCLabTest, QCInspection,
    AlertLog, SegregasiAcknowledgement
)

# Dependency injection for database sessions
def get_db():
    """
    Database session dependency
    Usage: def my_endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()