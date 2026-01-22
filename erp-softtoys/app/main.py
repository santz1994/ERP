from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.core.config import settings
from app.core.audit_middleware import AuditContextMiddleware

# Import all models to register them with Base before creating tables
# This must be done before Base.metadata.create_all()
from app.core import models  # noqa: F401

from app.api.v1 import (
    auth, ppic, warehouse, admin, websocket, 
    kanban, reports, import_export, embroidery,
    purchasing, finishgoods, report_builder, barcode, audit, dashboard,
    qa_convenience_endpoints
)
from app.modules.cutting import cutting_router
from app.modules.sewing import sewing_router
from app.modules.finishing import finishing_router
from app.modules.packing import packing_router
from app.modules.quality import quality_router

# Initialize Audit Trail Event Listeners
from app.core.audit_listeners import setup_audit_listeners

# Create Tables (Otomatis buat tabel saat start - untuk dev mode)
# Skip database creation if connection fails (useful for dev without DB)
try:
    Base.metadata.create_all(bind=engine)
    # Initialize audit listeners after tables are created
    setup_audit_listeners()
except Exception as e:
    print(f"⚠️  Warning: Could not create tables. Make sure PostgreSQL is running.")
    print(f"   Error: {str(e)[:100]}")
    print(f"   API will still start, but database operations will fail until DB is available.")

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Audit Context Middleware (First - captures user info)
app.add_middleware(AuditContextMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include API v1 Routers
app.include_router(
    auth.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    admin.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    ppic.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    warehouse.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    purchasing.router,
    prefix=settings.API_PREFIX
)

# Audit Trail Module (ISO 27001 A.12.4.1 Compliance)
app.include_router(
    audit.router,
    prefix=settings.API_PREFIX
)

# Dashboard Module (Optimized with Materialized Views)
app.include_router(
    dashboard.router,
    prefix=settings.API_PREFIX
)

# Phase 2: Production Module Routers
app.include_router(
    cutting_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    embroidery.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    sewing_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    finishing_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    packing_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    finishgoods.router,
    prefix=settings.API_PREFIX
)

# Phase 3: Quality Control Module
app.include_router(
    quality_router,
    prefix=settings.API_PREFIX
)

# WebSocket for real-time notifications
app.include_router(
    websocket.router,
    prefix=settings.API_PREFIX
)

# E-Kanban for accessory requests
app.include_router(
    kanban.router,
    prefix=settings.API_PREFIX
)

# Reporting Module (PDF/Excel)
app.include_router(
    reports.router,
    prefix=settings.API_PREFIX
)

# Import/Export Module (CSV/Excel)
app.include_router(
    import_export.router,
    prefix=settings.API_PREFIX
)

# Dynamic Report Builder
app.include_router(
    report_builder.router,
    prefix=settings.API_PREFIX
)

# Barcode Scanner Module
app.include_router(
    barcode.router,
    prefix=settings.API_PREFIX
)

# QA Convenience Endpoints (for testing)
app.include_router(
    qa_convenience_endpoints.router,
    prefix=settings.API_PREFIX
)

@app.get("/")
def read_root():
    """Root endpoint - System health check"""
    return {
        "message": "ERP Quty Karunia Running",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "api_prefix": settings.API_PREFIX
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }