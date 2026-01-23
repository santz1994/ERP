"""Finishing Module Package
Production department for product completion: stuffing, closing, QC, and conversion to Finish Good
"""

from app.modules.finishing.router import router as finishing_router

__all__ = ["finishing_router"]
