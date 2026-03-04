"""Authentication API Endpoints (Phase 1)
User registration, login, token management, profile.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.models.users import User
from app.core.models.users import UserRole as UserRoleModel
from app.core.schemas import AuthResponse, TokenResponse, UserCreate, UserLogin, UserResponse
from app.core.security import PasswordUtils, TokenUtils

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}, 403: {"description": "Forbidden"}}
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user.

    **Roles Required**: None (public endpoint)

    **Request Body**:
    - `username`: Unique username (3-50 chars)
    - `email`: Valid email address
    - `password`: Password (min 8 chars)
    - `full_name`: User full name
    - `roles`: List of roles (default: warehouse_op)

    **Responses**:
    - `201`: User created successfully
    - `400`: Username or email already exists
    - `422`: Validation error

    **Default Roles**:
    - admin_cutting, admin_sewing, admin_finishing, qc_inspector, etc.
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_password = PasswordUtils.hash_password(user_data.password)

    # Use first role from list or default (already a UserRole enum)
    user_role = user_data.roles[0] if user_data.roles else UserRoleModel.WAREHOUSE_OP

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_role,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role.value,  # Fixed: single role as string
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint.

    **Roles Required**: None (public endpoint)

    **Request Body**:
    - `username`: Username or email
    - `password`: User password

    **Responses**:
    - `200`: Login successful, returns access token and refresh token
    - `401`: Invalid credentials
    - `403`: Account inactive or locked
    - `429`: Too many login attempts (account locked 15 minutes)
    - `422`: Validation error

    **Token Format**:
    - Use `access_token` for API requests (Authorization: Bearer <token>)
    - Use `refresh_token` to get new access token when expired (24 hours validity)
    """
    try:
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == credentials.username) | (User.email == credentials.username)
        ).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving user"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check if account is locked (use timezone-naive datetime consistently)
    now = datetime.utcnow()
    if user.locked_until:
        # Ensure both datetimes are naive for comparison
        locked_until = user.locked_until.replace(tzinfo=None) if user.locked_until.tzinfo else user.locked_until
        if locked_until > now:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked. Try again after {locked_until}"
            )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive. Contact administrator."
        )

    # Verify password
    try:
        password_valid = PasswordUtils.verify_password(credentials.password, user.hashed_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password verification error"
        )
    
    if not password_valid:
        # Increment failed attempts
        user.login_attempts += 1

        # Lock account after 5 failed attempts for 15 minutes
        if user.login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Account locked for 15 minutes."
            )

        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Reset failed attempts on successful login
    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()

    # Generate tokens with single role (not list)
    try:
        role_name = user.role.value  # Get the actual role value

        access_token = TokenUtils.create_access_token(
            user_id=user.id,
            username=user.username,
            email=user.email,
            roles=[role_name]
        )

        refresh_token = TokenUtils.create_refresh_token(
            user_id=user.id,
            username=user.username
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token generation error"
        )

    db.commit()

    # Return tokens with user data
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=24 * 3600,  # 24 hours in seconds
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token_str: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token.

    **Roles Required**: None

    **Query Parameters**:
    - `refresh_token_str`: Refresh token from login response

    **Responses**:
    - `200`: New access token returned
    - `401`: Invalid or expired refresh token
    """
    token_data = TokenUtils.decode_token(refresh_token_str)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Generate new access token
    role_name = user.role.value

    access_token = TokenUtils.create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        roles=[role_name]
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=24 * 3600
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information (OPTIMIZED for API-02 Test).

    **Performance Optimization:**
    - Direct object access (no additional DB query)
    - Current user already loaded from token verification
    - Response time target: < 100ms

    **Roles Required**: Any authenticated user

    **Responses**:
    - `200`: Current user information
    - `401`: Unauthorized

    **Test Scenario API-02:**
    - Expected response time: < 100ms (was 2.054s before optimization)
    - Optimization: Removed redundant queries, use cached user object
    """
    # Direct return - no additional DB query needed
    # User object already loaded and cached in get_current_user dependency
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


class PasswordChangeRequest(BaseModel):
    """Password change request."""

    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password.

    **Roles Required**: Any authenticated user

    **Request Body**:
    - `old_password`: Current password
    - `new_password`: New password (min 8 chars)

    **Responses**:
    - `200`: Password changed successfully
    - `401`: Old password incorrect
    - `422`: Validation error
    """
    # Verify old password
    if not PasswordUtils.verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect"
        )

    # Hash new password
    new_hashed = PasswordUtils.hash_password(request.new_password)

    # Update user
    current_user.hashed_password = new_hashed
    current_user.last_password_change = datetime.utcnow()

    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint.

    **Roles Required**: Any authenticated user

    **Responses**:
    - `200`: Logged out successfully
    - `401`: Unauthorized

    **Note**: Client should discard the access token after calling this endpoint
    """
    return {
        "message": "Logged out successfully",
        "username": current_user.username
    }


# ── Permission code map: (ModuleName, Permission) → list of frontend codes ──
from app.core.permissions import ROLE_PERMISSIONS, ModuleName, Permission as Perm

_MODULE_ACTION_CODES: dict[tuple, list[str]] = {
    # Dashboard
    (ModuleName.DASHBOARD, Perm.VIEW): ["dashboard.view_stats", "dashboard.view_kpi"],

    # PPIC
    (ModuleName.PPIC, Perm.VIEW): ["ppic.view_mo", "ppic.view_spk", "ppic.view_status"],
    (ModuleName.PPIC, Perm.CREATE): ["ppic.create_mo", "ppic.request_material"],
    (ModuleName.PPIC, Perm.UPDATE): ["ppic.update_mo"],
    (ModuleName.PPIC, Perm.APPROVE): ["ppic.approve_mo"],

    # Purchasing
    (ModuleName.PURCHASING, Perm.VIEW): ["purchasing.view_po", "purchasing.view_requests"],
    (ModuleName.PURCHASING, Perm.CREATE): ["purchasing.create_po", "purchasing.request_material"],
    (ModuleName.PURCHASING, Perm.UPDATE): ["purchasing.update_po"],
    (ModuleName.PURCHASING, Perm.APPROVE): ["purchasing.approve_po"],

    # Warehouse
    (ModuleName.WAREHOUSE, Perm.VIEW): ["warehouse.view_stock", "warehouse.view_receipts", "warehouse.view_issues"],
    (ModuleName.WAREHOUSE, Perm.CREATE): ["warehouse.stock_in", "warehouse.stock_out"],
    (ModuleName.WAREHOUSE, Perm.UPDATE): ["warehouse.update_stock"],
    (ModuleName.WAREHOUSE, Perm.EXECUTE): ["warehouse.stock_in", "warehouse.stock_out", "warehouse.transfer"],
    (ModuleName.WAREHOUSE, Perm.APPROVE): ["warehouse.approve_adjustment"],

    # Cutting
    (ModuleName.CUTTING, Perm.VIEW): ["cutting.view_status", "cutting.view_wo", "cutting.view_schedule"],
    (ModuleName.CUTTING, Perm.CREATE): ["cutting.allocate_material"],
    (ModuleName.CUTTING, Perm.EXECUTE): ["cutting.allocate_material", "cutting.complete_operation", "cutting.transfer_to_next"],
    (ModuleName.CUTTING, Perm.APPROVE): ["cutting.approve_wo", "cutting.handle_shortage"],

    # Embroidery
    (ModuleName.EMBROIDERY, Perm.VIEW): ["embroidery.view_status", "embroidery.view_wo"],
    (ModuleName.EMBROIDERY, Perm.CREATE): ["embroidery.allocate_material"],
    (ModuleName.EMBROIDERY, Perm.EXECUTE): ["embroidery.complete_operation"],

    # Sewing
    (ModuleName.SEWING, Perm.VIEW): ["sewing.view_status", "sewing.view_wo"],
    (ModuleName.SEWING, Perm.CREATE): ["sewing.create_transfer", "sewing.validate_input"],
    (ModuleName.SEWING, Perm.EXECUTE): [
        "sewing.accept_transfer", "sewing.process_stage",
        "sewing.inline_qc", "sewing.create_transfer", "sewing.return_to_stage",
    ],
    (ModuleName.SEWING, Perm.UPDATE): ["sewing.return_to_stage"],

    # Finishing
    (ModuleName.FINISHING, Perm.VIEW): ["finishing.view_status", "finishing.view_wo"],
    (ModuleName.FINISHING, Perm.EXECUTE): [
        "finishing.accept_transfer", "finishing.line_clearance", "finishing.perform_stuffing",
    ],

    # Packing
    (ModuleName.PACKING, Perm.VIEW): ["packing.view_status", "packing.view_wo"],
    (ModuleName.PACKING, Perm.CREATE): ["packing.create_request"],
    (ModuleName.PACKING, Perm.EXECUTE): [
        "packing.sort_by_destination", "packing.pack_product",
        "packing.label_carton", "packing.complete_operation",
    ],

    # Finish Goods
    (ModuleName.FINISHGOODS, Perm.VIEW): ["finishgoods.view_stock", "finishgoods.view_shipments"],
    (ModuleName.FINISHGOODS, Perm.CREATE): ["finishgoods.receive"],
    (ModuleName.FINISHGOODS, Perm.EXECUTE): ["finishgoods.ship", "finishgoods.receive"],

    # QC
    (ModuleName.QC, Perm.VIEW): ["qc.view_reports", "qc.view_checkpoints"],
    (ModuleName.QC, Perm.CREATE): ["qc.inspect", "qc.record_result"],
    (ModuleName.QC, Perm.APPROVE): ["qc.approve_result", "qc.lab_test"],

    # Kanban
    (ModuleName.KANBAN, Perm.VIEW): ["kanban.view_requests"],
    (ModuleName.KANBAN, Perm.CREATE): ["kanban.create_request"],
    (ModuleName.KANBAN, Perm.APPROVE): ["kanban.approve_request", "kanban.fulfill_request"],

    # Reports
    (ModuleName.REPORTS, Perm.VIEW): [
        "reports.view_production", "reports.view_inventory",
        "reports.view_qc", "reports.view_financial",
    ],
    (ModuleName.REPORTS, Perm.CREATE): ["reports.export", "reports.generate"],

    # Admin
    (ModuleName.ADMIN, Perm.VIEW): ["admin.view_users", "admin.view_system_info"],
    (ModuleName.ADMIN, Perm.CREATE): ["admin.create_user"],
    (ModuleName.ADMIN, Perm.UPDATE): ["admin.manage_users", "admin.manage_permissions", "admin.manage_system"],
    (ModuleName.ADMIN, Perm.DELETE): ["admin.delete_user"],

    # Import/Export
    (ModuleName.IMPORT_EXPORT, Perm.VIEW): ["import_export.view_history"],
    (ModuleName.IMPORT_EXPORT, Perm.CREATE): ["import_export.import_data", "import_export.export_data"],

    # Masterdata
    (ModuleName.MASTERDATA, Perm.VIEW): ["masterdata.view_products", "masterdata.view_categories", "masterdata.view_suppliers"],
    (ModuleName.MASTERDATA, Perm.CREATE): ["masterdata.create_product", "masterdata.create_category"],
    (ModuleName.MASTERDATA, Perm.UPDATE): ["masterdata.update_product", "masterdata.update_category"],
    (ModuleName.MASTERDATA, Perm.DELETE): ["masterdata.delete_product"],

    # Audit
    (ModuleName.AUDIT, Perm.VIEW): ["audit.view_logs", "audit.view_user_activity", "audit.view_security_logs"],
    (ModuleName.AUDIT, Perm.CREATE): ["audit.export_logs"],

    # Barcode
    (ModuleName.BARCODE, Perm.VIEW): ["barcode.view"],
    (ModuleName.BARCODE, Perm.EXECUTE): ["barcode.scan"],
}

_PRODUCTION_DEPT_MODULES = [
    ModuleName.CUTTING, ModuleName.EMBROIDERY,
    ModuleName.SEWING, ModuleName.FINISHING, ModuleName.PACKING,
]

_ALL_PERMISSION_CODES: list[str] = sorted({
    code
    for codes in _MODULE_ACTION_CODES.values()
    for code in codes
} | {"production.view_status", "production.view_wip", "production.schedule_production", "production.input_daily"})


def _compute_permission_codes(user_role: "UserRoleModel") -> list[str]:
    """Compute the complete list of frontend permission codes for a given role."""
    from app.core.models.users import UserRole as _UR
    # Bypass roles get all codes
    if user_role in (_UR.SUPERADMIN, _UR.DEVELOPER, _UR.ADMIN, _UR.MANAGER):
        return _ALL_PERMISSION_CODES

    role_perms = ROLE_PERMISSIONS.get(user_role, {})
    codes: set[str] = set()
    has_dept_view = False
    has_dept_input = False

    for module, permitted in role_perms.items():
        for perm in permitted:
            codes.update(_MODULE_ACTION_CODES.get((module, perm), []))

        if module in _PRODUCTION_DEPT_MODULES:
            if Perm.VIEW in permitted:
                has_dept_view = True
            if Perm.CREATE in permitted or Perm.EXECUTE in permitted:
                has_dept_input = True

    if has_dept_view:
        codes.update(["production.view_status", "production.view_wip", "production.schedule_production"])
    if has_dept_input:
        codes.add("production.input_daily")

    return sorted(codes)


@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's permissions summary (PBAC — Permission-Based Access Control).

    **Roles Required**: Any authenticated user
    Returns a role-derived list of permission codes used by the frontend
    for sidebar visibility and route guards.

    **Response Format**:
    ```json
    {
        "user_id": 1,
        "username": "john.doe",
        "role": "PPIC Manager",
        "is_active": true,
        "permissions": ["dashboard.view_stats", "ppic.view_mo", ...]
    }
    ```
    """
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "permissions": _compute_permission_codes(current_user.role),
    }

