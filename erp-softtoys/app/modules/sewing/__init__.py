"""
Sewing Module Package
Production department for material assembly, labeling, and stitching
Implements 3-stage process with inline QC and segregation protocol
"""

from app.modules.sewing.router import router as sewing_router

__all__ = ["sewing_router"]
