"""Cutting Module Package
Production department for material cutting from rolls to pieces
Implements QT-09 line clearance protocol for transfer to Sewing/Embroidery.
"""

from app.modules.cutting.router import router as cutting_router

__all__ = ["cutting_router"]
