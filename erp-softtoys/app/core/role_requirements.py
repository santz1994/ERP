"""Role Requirements for API Endpoints
Centralized role-based access control mapping
ISO 27001 Compliant - Segregation of Duties (SoD)
"""

from typing import list

from app.core.models.users import UserRole


class EndpointRoleRequirements:
    """Centralized role requirements for all API endpoints
    Based on SEGREGATION_OF_DUTIES_MATRIX.md
    """

    # PPIC Module - Manufacturing Orders & Planning
    PPIC_CREATE = [
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN, UserRole.ADMIN
    ]
    PPIC_READ = [
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN, UserRole.ADMIN,
        UserRole.SPV_CUTTING, UserRole.SPV_SEWING, UserRole.SPV_FINISHING
    ]
    PPIC_APPROVE = [UserRole.PPIC_MANAGER, UserRole.ADMIN]

    # Purchasing Module
    PURCHASING_CREATE = [
        UserRole.PURCHASING, UserRole.PURCHASING_HEAD, UserRole.ADMIN
    ]
    PURCHASING_APPROVE = [
        UserRole.PURCHASING_HEAD, UserRole.MANAGER, UserRole.ADMIN
    ]
    PURCHASING_READ = [
        UserRole.PURCHASING, UserRole.PURCHASING_HEAD, UserRole.ADMIN,
        UserRole.WAREHOUSE_ADMIN, UserRole.FINANCE_MANAGER
    ]

    # Warehouse Module
    WAREHOUSE_CREATE = [
        UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP, UserRole.ADMIN
    ]
    WAREHOUSE_APPROVE = [UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN]
    WAREHOUSE_READ = [
        UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP, UserRole.ADMIN,
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN
    ]

    # Cutting Module
    CUTTING_EXECUTE = [
        UserRole.OPERATOR_CUT, UserRole.SPV_CUTTING, UserRole.ADMIN
    ]
    CUTTING_APPROVE = [UserRole.SPV_CUTTING, UserRole.ADMIN]
    CUTTING_READ = [
        UserRole.OPERATOR_CUT, UserRole.SPV_CUTTING, UserRole.ADMIN,
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN
    ]

    # Embroidery Module
    EMBROIDERY_EXECUTE = [
        UserRole.OPERATOR_EMBRO, UserRole.SPV_CUTTING, UserRole.ADMIN
    ]
    EMBROIDERY_READ = [
        UserRole.OPERATOR_EMBRO, UserRole.SPV_CUTTING, UserRole.ADMIN,
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN
    ]

    # Sewing Module
    SEWING_EXECUTE = [
        UserRole.OPERATOR_SEW, UserRole.SPV_SEWING, UserRole.ADMIN
    ]
    SEWING_APPROVE = [UserRole.SPV_SEWING, UserRole.ADMIN]
    SEWING_READ = [
        UserRole.OPERATOR_SEW, UserRole.SPV_SEWING, UserRole.ADMIN,
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN
    ]

    # Finishing Module
    FINISHING_EXECUTE = [
        UserRole.OPERATOR_FINISH, UserRole.SPV_FINISHING, UserRole.ADMIN
    ]
    FINISHING_APPROVE = [UserRole.SPV_FINISHING, UserRole.ADMIN]
    FINISHING_READ = [
        UserRole.OPERATOR_FINISH, UserRole.SPV_FINISHING, UserRole.ADMIN,
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN
    ]

    # Packing Module
    PACKING_EXECUTE = [UserRole.OPERATOR_PACK, UserRole.ADMIN]
    PACKING_READ = [
        UserRole.OPERATOR_PACK, UserRole.ADMIN, UserRole.WAREHOUSE_ADMIN,
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN
    ]

    # Quality Control Module
    QC_INSPECT = [UserRole.QC_INSPECTOR, UserRole.QC_LAB, UserRole.ADMIN]
    QC_LAB_TEST = [UserRole.QC_LAB, UserRole.ADMIN]
    QC_APPROVE = [UserRole.QC_LAB, UserRole.ADMIN]
    QC_READ = [
        UserRole.QC_INSPECTOR, UserRole.QC_LAB, UserRole.ADMIN,
        UserRole.SPV_CUTTING, UserRole.SPV_SEWING, UserRole.SPV_FINISHING
    ]

    # Finish Goods Module
    FINISHGOODS_CREATE = [
        UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP, UserRole.ADMIN
    ]
    FINISHGOODS_READ = [
        UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP, UserRole.ADMIN,
        UserRole.PPIC_MANAGER, UserRole.SECURITY
    ]
    FINISHGOODS_SHIP = [
        UserRole.WAREHOUSE_ADMIN, UserRole.SECURITY, UserRole.ADMIN
    ]

    # Kanban Module
    KANBAN_CREATE = [
        UserRole.OPERATOR_PACK, UserRole.WAREHOUSE_OP, UserRole.ADMIN
    ]
    KANBAN_APPROVE = [UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN]
    KANBAN_FULFILL = [
        UserRole.WAREHOUSE_OP, UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN
    ]

    # Reports Module
    REPORTS_READ = [
        UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN, UserRole.MANAGER,
        UserRole.FINANCE_MANAGER, UserRole.ADMIN
    ]
    REPORTS_CREATE = [UserRole.PPIC_MANAGER, UserRole.ADMIN]

    # Admin Module - User Management
    ADMIN_USER_MANAGE = [UserRole.SUPERADMIN, UserRole.ADMIN]
    ADMIN_USER_CREATE = [UserRole.SUPERADMIN, UserRole.ADMIN]
    ADMIN_USER_DELETE = [UserRole.SUPERADMIN]  # Only Superadmin can delete

    # Admin Module - Masterdata
    ADMIN_MASTERDATA_MANAGE = [UserRole.ADMIN, UserRole.PPIC_MANAGER]
    ADMIN_MASTERDATA_READ = [
        UserRole.ADMIN, UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN,
        UserRole.PURCHASING, UserRole.WAREHOUSE_ADMIN
    ]

    # Admin Module - Import/Export
    ADMIN_IMPORT = [UserRole.ADMIN]
    ADMIN_EXPORT = [
        UserRole.ADMIN, UserRole.PPIC_MANAGER, UserRole.WAREHOUSE_ADMIN,
        UserRole.FINANCE_MANAGER
    ]

    # Audit Trail - Read Only for Auditors
    AUDIT_READ = [UserRole.DEVELOPER, UserRole.SUPERADMIN, UserRole.MANAGER,
                  UserRole.FINANCE_MANAGER, UserRole.ADMIN]

    # Barcode Scanner - All Production Operators
    BARCODE_SCAN = [UserRole.WAREHOUSE_OP, UserRole.WAREHOUSE_ADMIN,
                    UserRole.OPERATOR_CUT, UserRole.OPERATOR_EMBRO,
                    UserRole.OPERATOR_SEW, UserRole.OPERATOR_FINISH,
                    UserRole.OPERATOR_PACK, UserRole.ADMIN]


# Helper function to convert role list to role name strings
def get_role_names(roles: list[UserRole]) -> list[str]:
    """Convert UserRole enum list to role name strings"""
    return [role.value for role in roles]


# Endpoint to Role Mapping (for documentation and validation)
ENDPOINT_ROLE_MAP: Dict[str, Dict[str, List[UserRole]]] = {
    "ppic": {
        "create_mo": EndpointRoleRequirements.PPIC_CREATE,
        "approve_mo": EndpointRoleRequirements.PPIC_APPROVE,
        "list_mo": EndpointRoleRequirements.PPIC_READ,
        "explode_bom": EndpointRoleRequirements.PPIC_CREATE,
    },
    "purchasing": {
        "create_po": EndpointRoleRequirements.PURCHASING_CREATE,
        "approve_po": EndpointRoleRequirements.PURCHASING_APPROVE,
        "list_po": EndpointRoleRequirements.PURCHASING_READ,
        "receive_po": EndpointRoleRequirements.WAREHOUSE_CREATE,
    },
    "warehouse": {
        "stock_in": EndpointRoleRequirements.WAREHOUSE_CREATE,
        "stock_out": EndpointRoleRequirements.WAREHOUSE_CREATE,
        "stock_adjustment": EndpointRoleRequirements.WAREHOUSE_APPROVE,
        "inventory_report": EndpointRoleRequirements.WAREHOUSE_READ,
    },
    "cutting": {
        "start_work": EndpointRoleRequirements.CUTTING_EXECUTE,
        "complete_work": EndpointRoleRequirements.CUTTING_EXECUTE,
        "handle_shortage": EndpointRoleRequirements.CUTTING_APPROVE,
        "transfer": EndpointRoleRequirements.CUTTING_APPROVE,
    },
    "embroidery": {
        "start_work": EndpointRoleRequirements.EMBROIDERY_EXECUTE,
        "complete_work": EndpointRoleRequirements.EMBROIDERY_EXECUTE,
        "transfer": EndpointRoleRequirements.EMBROIDERY_EXECUTE,
    },
    "sewing": {
        "accept_transfer": EndpointRoleRequirements.SEWING_EXECUTE,
        "process_stage": EndpointRoleRequirements.SEWING_EXECUTE,
        "qc_inspect": EndpointRoleRequirements.SEWING_EXECUTE,
        "transfer": EndpointRoleRequirements.SEWING_APPROVE,
    },
    "finishing": {
        "stuffing": EndpointRoleRequirements.FINISHING_EXECUTE,
        "metal_detector": EndpointRoleRequirements.FINISHING_EXECUTE,
        "convert_to_fg": EndpointRoleRequirements.FINISHING_APPROVE,
    },
    "packing": {
        "sort_destination": EndpointRoleRequirements.PACKING_EXECUTE,
        "package_cartons": EndpointRoleRequirements.PACKING_EXECUTE,
        "shipping_mark": EndpointRoleRequirements.PACKING_EXECUTE,
    },
    "quality": {
        "lab_test": EndpointRoleRequirements.QC_LAB_TEST,
        "inline_inspect": EndpointRoleRequirements.QC_INSPECT,
        "metal_detector_scan": EndpointRoleRequirements.QC_INSPECT,
        "approve_batch": EndpointRoleRequirements.QC_APPROVE,
    },
    "finishgoods": {
        "receive_from_packing": EndpointRoleRequirements.FINISHGOODS_CREATE,
        "prepare_shipment": EndpointRoleRequirements.FINISHGOODS_CREATE,
        "ship": EndpointRoleRequirements.FINISHGOODS_SHIP,
        "inventory": EndpointRoleRequirements.FINISHGOODS_READ,
    },
    "kanban": {
        "create_card": EndpointRoleRequirements.KANBAN_CREATE,
        "approve_card": EndpointRoleRequirements.KANBAN_APPROVE,
        "fulfill_card": EndpointRoleRequirements.KANBAN_FULFILL,
    },
    "reports": {
        "production_report": EndpointRoleRequirements.REPORTS_READ,
        "qc_report": EndpointRoleRequirements.REPORTS_READ,
        "inventory_report": EndpointRoleRequirements.REPORTS_READ,
        "create_template": EndpointRoleRequirements.REPORTS_CREATE,
    },
    "admin": {
        "list_users": EndpointRoleRequirements.ADMIN_USER_MANAGE,
        "create_user": EndpointRoleRequirements.ADMIN_USER_CREATE,
        "delete_user": EndpointRoleRequirements.ADMIN_USER_DELETE,
        "import_data": EndpointRoleRequirements.ADMIN_IMPORT,
        "export_data": EndpointRoleRequirements.ADMIN_EXPORT,
    },
    "audit": {
        "list_logs": EndpointRoleRequirements.AUDIT_READ,
        "search_logs": EndpointRoleRequirements.AUDIT_READ,
    },
    "barcode": {
        "validate": EndpointRoleRequirements.BARCODE_SCAN,
        "receive": EndpointRoleRequirements.BARCODE_SCAN,
        "pick": EndpointRoleRequirements.BARCODE_SCAN,
    },
}
