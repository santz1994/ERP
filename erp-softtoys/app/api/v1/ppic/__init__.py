"""
PPIC (Production Planning & Inventory Control) Module API Routers
Contains all PPIC-related endpoints
"""
from . import daily_production
from . import dashboard

# Export the routers from sub-modules - they already have /ppic prefix
router = daily_production.router

__all__ = ["router", "daily_production", "dashboard"]
