"""Embroidery Module Router
API endpoints for embroidery operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.models.users import User
from .embroidery_service import EmbroideryService

router = APIRouter(prefix="/embroidery", tags=["embroidery"])


@router.get("/line-status")
async def get_line_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get embroidery line status
    Returns occupancy of embroidery lines
    """
    try:
        service = EmbroideryService(db)
        line_status = service.get_line_status()
        
        # Transform to response format
        lines = []
        for item in line_status:
            lines.append({
                "line_id": item.line_id if hasattr(item, 'line_id') else 1,
                "line_name": f"Embroidery Line {item.line_id if hasattr(item, 'line_id') else 1}",
                "status": item.status if hasattr(item, 'status') else "idle",
                "current_wo_id": item.work_order_id if hasattr(item, 'work_order_id') else None,
                "occupancy": getattr(item, 'occupancy', 0),
                "utilization_pct": getattr(item, 'utilization_pct', 0)
            })
        
        return {
            "success": True,
            "data": lines,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting embroidery line status: {str(e)}"
        )


@router.get("/work-orders")
async def get_work_orders(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get embroidery work orders
    """
    try:
        service = EmbroideryService(db)
        work_orders = service.get_work_orders(status)
        
        return {
            "success": True,
            "data": [
                {
                    "id": wo.id,
                    "batch_number": wo.batch_number,
                    "product": wo.product_id,
                    "qty_planned": getattr(wo, 'target_qty', 0),
                    "qty_produced": getattr(wo, 'actual_qty', 0),
                    "status": wo.status if hasattr(wo, 'status') else "pending"
                }
                for wo in work_orders
            ],
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting work orders: {str(e)}"
        )
