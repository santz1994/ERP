from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry
import time

from app.api.v1 import (
    admin,
    audit,
    auth,
    barcode,
    dashboard,
    embroidery,
    finishgoods,
    import_export,
    imports,  # ✅ NEW: Masterdata Imports (Session 49 Phase 8)
    kanban,
    material_allocation,  # ✅ NEW: Material Allocation API
    pallet,  # ✅ NEW: Pallet System API (2026-02-10)
    ppic,
    purchasing,
    qa_convenience_endpoints,
    report_builder,
    reports,
    websocket,
)
# Import warehouse from warehouse_endpoints module
from app.api.v1 import warehouse_endpoints as warehouse

# Import production module routers
from app.api.v1.production import daily_input as production_daily_input
from app.api.v1.production import approval as production_approval
from app.api.v1.production import spk_edit as production_spk_edit
from app.api.v1.production import work_orders as production_work_orders
from app.api.v1.production import production_execution
from app.api.v1.ppic import daily_production as ppic_daily_production
from app.api.v1.ppic import dashboard as ppic_dashboard
from app.api.v1.ppic import reports as ppic_reports

# Import all models to register them with Base before creating tables
# This must be done before Base.metadata.create_all()
from app.core import models  # noqa: F401

# Initialize Audit Trail Event Listeners
from app.core.audit_listeners import setup_audit_listeners
from app.core.audit_middleware import AuditContextMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.core.datetime_utils import DateTimeJSONEncoder
from app.modules.cutting import cutting_router
from app.modules.finishing import finishing_router
from app.modules.packing import packing_router
from app.modules.quality import quality_router
from app.modules.sewing import sewing_router

# Create Tables (Otomatis buat tabel saat start - untuk dev mode)
# Skip database creation if connection fails (useful for dev without DB)
try:
    Base.metadata.create_all(bind=engine)
    # Initialize audit listeners after tables are created
    setup_audit_listeners()
except Exception:
    pass

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    json_encoder=DateTimeJSONEncoder
)

# ============================================================================
# Prometheus Metrics Configuration
# ============================================================================
registry = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# Database metrics
DB_CONNECTIONS = Counter(
    'database_connections_total',
    'Total database connections',
    ['status'],
    registry=registry
)

# Application metrics
API_ERRORS = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type'],
    registry=registry
)

# ============================================================================
# Prometheus Middleware
# ============================================================================
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Track request
        try:
            response = await call_next(request)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            # Track latency
            process_time = time.time() - start_time
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(process_time)
            
            return response
        except Exception as e:
            API_ERRORS.labels(
                endpoint=request.url.path,
                error_type=type(e).__name__
            ).inc()
            raise

app.add_middleware(PrometheusMiddleware)

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

# PPIC Sub-modules (Session 31)
app.include_router(
    ppic_daily_production.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    ppic_dashboard.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    ppic_reports.router,
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

# Production Daily Input & Approval Workflow (Session 31)
app.include_router(
    production_daily_input.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    production_approval.router,
    prefix=settings.API_PREFIX
)

# Production SPK Edit Workflow (Session 37, Feature #7)
app.include_router(
    production_spk_edit.router,
    prefix=settings.API_PREFIX
)

# Work Orders API (BOM Explosion & WO Generation)
app.include_router(
    production_work_orders.router,
    prefix=settings.API_PREFIX
)

# Production Execution API (Daily Input, WIP Transfer)
app.include_router(
    production_execution.router,
    prefix=settings.API_PREFIX
)

# ✅ Material Allocation API (Week 3-4 Implementation)
app.include_router(
    material_allocation.router,
    # Note: material_allocation.router already has prefix="/api/v1/material-allocation"
    # so we don't add settings.API_PREFIX here
)

# Phase 3: Quality Control Module
app.include_router(
    quality_router,
    prefix=settings.API_PREFIX
)

# ✅ Pallet System API (2026-02-10)
app.include_router(
    pallet.router,
    # Note: pallet.router already has prefix="/api/v1/pallet"
    # so we don't add settings.API_PREFIX here
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

# ✅ Masterdata Bulk Import Module (Session 49 Phase 8)
app.include_router(
    imports.router,
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
    """Root endpoint - System health check."""
    return {
        "message": "ERP Quty Karunia Running",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "api_prefix": settings.API_PREFIX
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint.
    
    Exposes application metrics for Prometheus scraping.
    Used by monitoring systems like Prometheus and Grafana.
    """
    return generate_latest(registry)

