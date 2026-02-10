"""
Production Calendar API Endpoints
Provides calendar view of daily production per department
**SECURITY**: Department-based access control enforced
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.models import User
from app.core.models.users import UserRole

router = APIRouter(prefix="/production", tags=["production"])


def validate_department_access(user: User, requested_dept: str) -> None:
    """
    Validate user has access to requested department calendar.
    
    Access Rules:
    1. SUPERADMIN, DEVELOPER, ADMIN, MANAGER, PPIC_MANAGER → Full access
    2. Supervisors (SPV_*) → Only their department
    3. Operators (OPERATOR_*) → Only their department
    4. Others → Deny
    
    Args:
        user: Current authenticated user
        requested_dept: Department being requested (CUTTING, SEWING, etc.)
        
    Raises:
        HTTPException 403: If user doesn't have access
    """
    # Full access roles (management level)
    FULL_ACCESS_ROLES = [
        UserRole.SUPERADMIN,
        UserRole.DEVELOPER,
        UserRole.ADMIN,
        UserRole.MANAGER,
        UserRole.PPIC_MANAGER,
        UserRole.PPIC_ADMIN
    ]
    
    if user.role in FULL_ACCESS_ROLES:
        return  # Full access granted
    
    # Department-specific access validation
    if not user.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Department Access Denied",
                "message": "Your account has no assigned department. "
                           "Contact admin.",
                "required_department": requested_dept,
                "your_role": user.role.value
            }
        )
    
    # Normalize department names for comparison
    user_dept = user.department.upper().strip()
    requested_dept_normalized = requested_dept.upper().strip()
    
    if user_dept != requested_dept_normalized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Department Access Denied",
                "message": f"You can only access {user_dept} calendar data.",
                "requested_department": requested_dept,
                "your_department": user.department,
                "your_role": user.role.value,
                "help": "Contact manager for cross-department access."
            }
        )


@router.get("/calendar")
async def get_production_calendar(
    department: str = Query(
        ...,
        description="Department: CUTTING, EMBROIDERY, SEWING, "
        "FINISHING, PACKING"
    ),
    month: str = Query(..., description="Month in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, List[dict]]:
    """
    Get production calendar data for a specific department and month.
    
    **Security**: Department-based access control enforced.
    - Management roles: Access all departments
    - Department staff: Access only their own department
    
    Returns:
        Dictionary mapping dates to daily production records
        Format: {
            "2026-02-01": [
                {
                    date, spkNumber, articleCode,
                    goodOutput, defectQty, targetDaily,
                    achievementPercent
                }
            ]
        }
    """
    # Validate department access (raises 403 if denied)
    validate_department_access(current_user, department)
    # Future implementation should:
    # 1. Query SPKDailyProduction table for month and department
    # 2. Group by date
    # 3. Calculate achievement percentages
    # 4. Return structured data
    
    return {}
