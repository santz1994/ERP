"""
Admin API Endpoints (Phase 1)
User management - create, update, deactivate, role assignment
Restricted to Admin role only
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models.users import User, UserRole
from app.core.dependencies import get_current_user, require_permission
from app.core.security import PasswordUtils
from app.core.schemas import UserResponse


router = APIRouter(
    prefix="/admin",
    tags=["Admin Management"],
    responses={403: {"description": "Forbidden - Admin only"}}
)


class UserUpdateRequest(BaseModel):
    """Update user request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = None
    department: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
    """User list response"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime


@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    current_user: User = Depends(require_permission("admin.manage_users")),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all users (Admin only)
    
    **Roles Required**: Admin
    
    **Query Parameters**:
    - `skip`: Number of users to skip (default: 0)
    - `limit`: Maximum users to return (default: 100, max: 1000)
    
    **Responses**:
    - `200`: List of users
    - `403`: Forbidden (Admin only)
    """
    users = db.query(User).offset(skip).limit(min(limit, 1000)).all()
    
    return [
        UserListResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            role=u.role.value,
            department=u.department,
            is_active=u.is_active,
            last_login=u.last_login,
            created_at=u.created_at
        )
        for u in users
    ]


@router.get("/users/{user_id}", response_model=UserListResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("admin.manage_users")),
    db: Session = Depends(get_db)
):
    """
    Get user details (Admin only)
    
    **Roles Required**: Admin
    
    **Path Parameters**:
    - `user_id`: User ID
    
    **Responses**:
    - `200`: User details
    - `403`: Forbidden
    - `404`: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserListResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        department=user.department,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at
    )


@router.put("/users/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user: User = Depends(require_permission("admin.manage_users")),
    db: Session = Depends(get_db)
):
    """
    Update user details (Admin only)
    
    **Roles Required**: Admin
    
    **Path Parameters**:
    - `user_id`: User ID
    
    **Request Body**:
    - `full_name`: New full name
    - `role`: New role (must be valid UserRole)
    - `department`: Department assignment
    - `is_active`: Active status
    
    **Responses**:
    - `200`: User updated
    - `403`: Forbidden
    - `404`: User not found
    - `400`: Invalid role
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if update_data.full_name:
        user.full_name = update_data.full_name
    
    if update_data.role:
        # Validate role
        try:
            user.role = UserRole[update_data.role.upper().replace("-", "_")]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {update_data.role}"
            )
    
    if update_data.department is not None:
        user.department = update_data.department
    
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserListResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        department=user.department,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at
    )


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_permission("admin.manage_users")),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account (Admin only)
    
    **Roles Required**: Admin
    
    **Path Parameters**:
    - `user_id`: User ID to deactivate
    
    **Responses**:
    - `200`: User deactivated
    - `403`: Forbidden
    - `404`: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )
    
    user.is_active = False
    db.commit()
    
    return {
        "message": f"User {user.username} deactivated",
        "user_id": user.id
    }


@router.post("/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: int,
    current_user: User = Depends(require_permission("admin.manage_users")),
    db: Session = Depends(get_db)
):
    """
    Reactivate user account (Admin only)
    
    **Roles Required**: Admin
    
    **Path Parameters**:
    - `user_id`: User ID to reactivate
    
    **Responses**:
    - `200`: User reactivated
    - `403`: Forbidden
    - `404`: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    user.login_attempts = 0  # Reset login attempts
    user.locked_until = None
    db.commit()
    
    return {
        "message": f"User {user.username} reactivated",
        "user_id": user.id
    }


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    current_user: User = Depends(require_permission("admin.manage_users")),
    db: Session = Depends(get_db)
):
    """
    Reset user password (Admin only)
    
    **Roles Required**: Admin
    
    **Path Parameters**:
    - `user_id`: User ID
    
    **Responses**:
    - `200`: Password reset, temporary password returned
    - `403`: Forbidden
    - `404`: User not found
    
    **Note**: Generates temporary password, user must change on first login
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate temporary password (12 chars random)
    import secrets
    temp_password = secrets.token_urlsafe(9)[:12]
    
    user.hashed_password = PasswordUtils.hash_password(temp_password)
    user.is_verified = False  # Force re-verification
    db.commit()
    
    return {
        "message": f"Password reset for {user.username}",
        "temporary_password": temp_password,
        "user_id": user.id,
        "note": "User must change password on next login"
    }


@router.get("/users/role/{role_name}")
async def list_users_by_role(
    role_name: str,
    current_user: User = Depends(require_permission("admin.manage_users")),
    db: Session = Depends(get_db)
):
    """
    List users by role (Admin only)
    
    **Roles Required**: Admin
    
    **Path Parameters**:
    - `role_name`: Role to filter by
    
    **Responses**:
    - `200`: List of users with given role
    - `403`: Forbidden
    - `400`: Invalid role
    """
    # Find users with this role
    users = db.query(User).filter(User.role.astext.ilike(f"%{role_name}%")).all()
    
    if not users:
        return []
    
    return [
        UserListResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            role=u.role.value,
            department=u.department,
            is_active=u.is_active,
            last_login=u.last_login,
            created_at=u.created_at
        )
        for u in users
    ]


@router.get("/environment-info")
async def get_environment_info(
    current_user: User = Depends(require_permission("admin.view_system_info"))
):
    """
    Get environment information and access control policies
    
    **Roles Required**: Admin
    
    **Use Case**: Debugging, security audit, compliance verification
    
    **Returns**:
    - Current environment (development/testing/production)
    - DEVELOPER role restrictions status
    - Allowed/blocked permissions for DEVELOPER
    - User's current role and restrictions
    """
    from app.core.environment_policy import get_environment_info, EnvironmentAccessControl
    from app.core.config import settings
    
    env_info = get_environment_info()
    
    # Add user-specific info
    env_info["current_user"] = {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.value,
        "is_developer": current_user.role == UserRole.DEVELOPER,
        "is_restricted": EnvironmentAccessControl.is_developer_in_production(current_user),
        "can_write": not EnvironmentAccessControl.is_developer_in_production(current_user)
    }
    
    env_info["security_settings"] = {
        "debug_mode": settings.DEBUG,
        "environment": settings.ENVIRONMENT.value,
        "jwt_expiration_hours": settings.JWT_EXPIRATION_HOURS
    }
    
    return env_info
