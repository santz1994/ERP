"""Quality Control Module
Handles QC Lab Testing, Inline Inspections, Metal Detector checks.
"""

from app.modules.quality.router import router as quality_router
from app.modules.quality.qc_checkpoint_router import router as qc_checkpoint_router

__all__ = ["quality_router", "qc_checkpoint_router"]
