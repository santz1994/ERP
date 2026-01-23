"""Quality Control Module
Handles QC Lab Testing, Inline Inspections, Metal Detector checks.
"""

from app.modules.quality.router import router as quality_router

__all__ = ["quality_router"]
