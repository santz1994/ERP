"""
PPIC (Production Planning & Inventory Control) Module API Routers
Contains all PPIC-related endpoints
"""
from . import daily_production
from . import dashboard

__all__ = ["daily_production", "dashboard"]
