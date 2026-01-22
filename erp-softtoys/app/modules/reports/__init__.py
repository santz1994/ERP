"""
Reports Module
Provides analytics and reporting endpoints for production, quality, and inventory
"""

from app.modules.reports.router import router as reports_router

__all__ = ["reports_router"]
