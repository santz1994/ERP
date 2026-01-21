"""
RBAC → PBAC Migration Script
=============================
Migrates existing Role-Based Access Control to Permission-Based
Access Control

Author: Daniel (IT Senior Developer)
Date: January 21, 2026
Version: 1.0

CRITICAL: This script performs breaking changes to the authorization
system. Always backup database before running!

Usage:
    python scripts/migrate_rbac_to_pbac.py

Features:
    - Creates permissions tables
    - Seeds 100+ permission definitions
    - Maps existing RBAC roles to PBAC permissions
    - Validates migration success
    - Automatic rollback on failure
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal  # noqa: E402
from app.core.models.users import UserRole  # noqa: E402


class PBACMigration:
    """Handles RBAC to PBAC migration with validation and rollback"""
    
    def __init__(self, db: Session):
        self.db = db
        self.migration_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log(self, message: str, level: str = "INFO"):
        """Log migration steps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = "✅" if level == "SUCCESS" else "📊" if level == "INFO" else "❌"
        print(f"[{timestamp}] {prefix} {message}")
    
    def create_permissions_tables(self) -> bool:
        """Step 1: Create PBAC database tables"""
        self.log("Creating permissions tables...", "INFO")
        
        try:
            sql = text("""
            -- Permissions master table
            CREATE TABLE IF NOT EXISTS permissions (
                id BIGSERIAL PRIMARY KEY,
                code VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                module VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT permissions_code_lowercase CHECK (code = LOWER(code))
            );
            
            CREATE INDEX IF NOT EXISTS idx_permissions_module ON permissions(module);
            CREATE INDEX IF NOT EXISTS idx_permissions_code ON permissions(code);
            
            -- Role-to-Permission mapping (default permissions per role)
            CREATE TABLE IF NOT EXISTS role_permissions (
                id BIGSERIAL PRIMARY KEY,
                role VARCHAR(50) NOT NULL,
                permission_id BIGINT REFERENCES permissions(id) ON DELETE CASCADE,
                granted_at TIMESTAMP DEFAULT NOW(),
                granted_by BIGINT REFERENCES users(id),
                UNIQUE(role, permission_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role);
            
            -- User-specific permission overrides
            CREATE TABLE IF NOT EXISTS user_custom_permissions (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                permission_id BIGINT REFERENCES permissions(id) ON DELETE CASCADE,
                is_granted BOOLEAN DEFAULT TRUE,
                granted_at TIMESTAMP DEFAULT NOW(),
                granted_by BIGINT REFERENCES users(id),
                expires_at TIMESTAMP NULL,
                reason TEXT,
                UNIQUE(user_id, permission_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_user_custom_perms_user ON user_custom_permissions(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_custom_perms_expiry ON user_custom_permissions(expires_at) 
                WHERE expires_at IS NOT NULL;
            
            -- Migration tracking table
            CREATE TABLE IF NOT EXISTS pbac_migrations (
                id BIGSERIAL PRIMARY KEY,
                migration_id VARCHAR(50) UNIQUE NOT NULL,
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP NULL,
                status VARCHAR(20) DEFAULT 'IN_PROGRESS',
                error_message TEXT NULL
            );
            
            INSERT INTO pbac_migrations (migration_id, status)
            VALUES (:migration_id, 'IN_PROGRESS');
            """)
            
            self.db.execute(sql, {"migration_id": self.migration_id})
            self.db.commit()
            
            self.log("Permissions tables created successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to create tables: {str(e)}", "ERROR")
            return False
    
    def seed_permissions(self) -> bool:
        """Step 2: Seed all permission definitions"""
        self.log("Seeding permission definitions...", "INFO")
        
        # Complete permission matrix (100+ permissions)
        permissions_data = [
            # Admin Module (13 permissions)
            ("admin.manage_users", "Manage Users", "Admin", "Create, edit, delete user accounts"),
            ("admin.delete_user", "Delete User", "Admin", "Permanently delete user accounts"),
            ("admin.reset_password", "Reset Password", "Admin", "Reset user passwords"),
            ("admin.assign_roles", "Assign Roles", "Admin", "Change user role assignments"),
            ("admin.view_audit_logs", "View Audit Logs", "Admin", "Access system audit trail"),
            ("admin.manage_masterdata", "Manage Master Data", "Admin", "Edit products, BOM, categories"),
            ("admin.import_data", "Import Data", "Admin", "Bulk import via Excel/CSV"),
            ("admin.export_data", "Export Data", "Admin", "Export data to Excel/CSV"),
            ("admin.system_config", "System Configuration", "Admin", "Modify system settings"),
            ("admin.backup_database", "Backup Database", "Admin", "Create database backups"),
            ("admin.restore_database", "Restore Database", "Admin", "Restore from backup"),
            ("admin.view_system_logs", "View System Logs", "Admin", "Access application logs"),
            ("admin.manage_security", "Manage Security", "Admin", "Security settings management"),
            
            # Purchasing Module (8 permissions)
            ("purchasing.create_po", "Create Purchase Order", "Purchasing", "Create new purchase orders"),
            ("purchasing.edit_po", "Edit Purchase Order", "Purchasing", "Modify draft purchase orders"),
            ("purchasing.approve_po", "Approve Purchase Order", "Purchasing", "Approve POs for sending"),
            ("purchasing.cancel_po", "Cancel Purchase Order", "Purchasing", "Cancel purchase orders"),
            ("purchasing.view_po", "View Purchase Order", "Purchasing", "View purchase order details"),
            ("purchasing.send_po", "Send Purchase Order", "Purchasing", "Send PO to supplier"),
            ("purchasing.receive_po", "Receive Purchase Order", "Purchasing", "Mark PO as received"),
            ("purchasing.vendor_management", "Vendor Management", "Purchasing", "Manage supplier data"),
            
            # Warehouse Module (12 permissions)
            ("warehouse.receive_goods", "Receive Goods", "Warehouse", "Receive incoming materials"),
            ("warehouse.adjust_stock", "Adjust Stock", "Warehouse", "Create stock adjustments"),
            ("warehouse.approve_adjustment", "Approve Adjustment", "Warehouse", "Approve stock adjustments"),
            ("warehouse.view_stock", "View Stock", "Warehouse", "View inventory levels"),
            ("warehouse.transfer_stock", "Transfer Stock", "Warehouse", "Transfer between locations"),
            ("warehouse.manage_locations", "Manage Locations", "Warehouse", "Create/edit locations"),
            ("warehouse.cycle_count", "Cycle Count", "Warehouse", "Perform stock counts"),
            ("warehouse.view_transactions", "View Transactions", "Warehouse", "View stock movement history"),
            ("warehouse.barcode_scan", "Barcode Scanning", "Warehouse", "Use barcode scanner"),
            ("warehouse.print_labels", "Print Labels", "Warehouse", "Print barcode labels"),
            ("warehouse.manage_lots", "Manage Lots", "Warehouse", "Lot/batch management"),
            ("warehouse.fifo_tracking", "FIFO Tracking", "Warehouse", "Track FIFO inventory"),
            
            # PPIC Module (10 permissions)
            ("ppic.create_mo", "Create Manufacturing Order", "PPIC", "Create new manufacturing orders"),
            ("ppic.edit_mo", "Edit Manufacturing Order", "PPIC", "Modify draft manufacturing orders"),
            ("ppic.approve_mo", "Approve Manufacturing Order", "PPIC", "Approve MOs for production"),
            ("ppic.cancel_mo", "Cancel Manufacturing Order", "PPIC", "Cancel manufacturing orders"),
            ("ppic.view_mo", "View Manufacturing Order", "PPIC", "View MO details"),
            ("ppic.explode_bom", "Explode BOM", "PPIC", "Generate material requirements from BOM"),
            ("ppic.plan_production", "Plan Production", "PPIC", "Create production schedules"),
            ("ppic.allocate_materials", "Allocate Materials", "PPIC", "Reserve materials for production"),
            ("ppic.view_capacity", "View Capacity", "PPIC", "View production capacity"),
            ("ppic.manage_bom", "Manage BOM", "PPIC", "Create/edit Bill of Materials"),
            
            # Cutting Module (8 permissions)
            ("cutting.execute", "Execute Cutting", "Cutting", "Perform cutting operations"),
            ("cutting.view_work_order", "View Work Order", "Cutting", "View cutting work orders"),
            ("cutting.create_transfer", "Create Transfer", "Cutting", "Create transfer to next dept"),
            ("cutting.approve_transfer", "Approve Transfer", "Cutting", "Approve outgoing transfers"),
            ("cutting.report_shortage", "Report Shortage", "Cutting", "Report material shortage"),
            ("cutting.report_surplus", "Report Surplus", "Cutting", "Report material surplus"),
            ("cutting.quality_check", "Quality Check", "Cutting", "Perform inline QC"),
            ("cutting.print_transfer_slip", "Print Transfer Slip", "Cutting", "Print QT-09 transfer slip"),
            
            # Embroidery Module (6 permissions)
            ("embroidery.execute", "Execute Embroidery", "Embroidery", "Perform embroidery operations"),
            ("embroidery.view_work_order", "View Work Order", "Embroidery", "View embroidery work orders"),
            ("embroidery.create_transfer", "Create Transfer", "Embroidery", "Create transfer to sewing"),
            ("embroidery.approve_transfer", "Approve Transfer", "Embroidery", "Approve transfers"),
            ("embroidery.manage_designs", "Manage Designs", "Embroidery", "Upload/edit embroidery designs"),
            ("embroidery.subcon_tracking", "Subcon Tracking", "Embroidery", "Track external embroidery"),
            
            # Sewing Module (10 permissions)
            ("sewing.execute", "Execute Sewing", "Sewing", "Perform sewing operations"),
            ("sewing.view_work_order", "View Work Order", "Sewing", "View sewing work orders"),
            ("sewing.create_transfer", "Create Transfer", "Sewing", "Create transfer to finishing"),
            ("sewing.approve_transfer", "Approve Transfer", "Sewing", "Approve transfers"),
            ("sewing.validate_bom", "Validate BOM", "Sewing", "Validate input vs BOM requirements"),
            ("sewing.segregate_defects", "Segregate Defects", "Sewing", "Separate defective items"),
            ("sewing.line_balancing", "Line Balancing", "Sewing", "Manage sewing line workload"),
            ("sewing.operator_performance", "Operator Performance", "Sewing", "Track operator efficiency"),
            ("sewing.quality_inline", "Inline QC", "Sewing", "Perform inline quality checks"),
            ("sewing.rework", "Rework Operations", "Sewing", "Handle rework items"),
            
            # Finishing Module (8 permissions)
            ("finishing.execute", "Execute Finishing", "Finishing", "Perform finishing operations"),
            ("finishing.stuffing", "Stuffing Operations", "Finishing", "Perform stuffing/filling"),
            ("finishing.closing", "Closing Operations", "Finishing", "Perform closing/sealing"),
            ("finishing.metal_detector", "Metal Detector", "Finishing", "Run metal detector QC"),
            ("finishing.convert_to_fg", "Convert to FG", "Finishing", "Convert WIP to Finish Goods"),
            ("finishing.view_work_order", "View Work Order", "Finishing", "View finishing work orders"),
            ("finishing.create_transfer", "Create Transfer", "Finishing", "Create transfer to packing"),
            ("finishing.approve_transfer", "Approve Transfer", "Finishing", "Approve transfers"),
            
            # Packing Module (7 permissions)
            ("packing.execute", "Execute Packing", "Packing", "Perform packing operations"),
            ("packing.view_work_order", "View Work Order", "Packing", "View packing work orders"),
            ("packing.create_carton", "Create Carton", "Packing", "Create master cartons"),
            ("packing.print_labels", "Print Labels", "Packing", "Print carton labels"),
            ("packing.shipping_mark", "Shipping Mark", "Packing", "Add shipping information"),
            ("packing.transfer_to_fg", "Transfer to FG", "Packing", "Transfer to Finish Goods warehouse"),
            ("packing.kanban_management", "Kanban Management", "Packing", "Manage kanban cards"),
            
            # Quality Module (12 permissions)
            ("qc.perform_lab_test", "Perform Lab Test", "Quality", "Execute lab tests (Drop, Seam, etc)"),
            ("qc.approve_batch", "Approve QC Batch", "Quality", "Approve batches after QC"),
            ("qc.reject_batch", "Reject QC Batch", "Quality", "Reject failed batches"),
            ("qc.view_inspections", "View Inspections", "Quality", "View QC inspection records"),
            ("qc.inline_inspection", "Inline Inspection", "Quality", "Perform inline QC checks"),
            ("qc.final_inspection", "Final Inspection", "Quality", "Final product inspection"),
            ("qc.defect_analysis", "Defect Analysis", "Quality", "Analyze defect patterns"),
            ("qc.upload_evidence", "Upload Evidence", "Quality", "Upload test photos/videos"),
            ("qc.manage_standards", "Manage Standards", "Quality", "Define quality standards"),
            ("qc.view_reports", "View QC Reports", "Quality", "Access quality reports"),
            ("qc.ncr_management", "NCR Management", "Quality", "Manage Non-Conformance Reports"),
            ("qc.capa_management", "CAPA Management", "Quality", "Corrective/Preventive Actions"),
            
            # Finish Goods Module (8 permissions)
            ("finishgoods.receive", "Receive Finish Goods", "FinishGoods", "Receive from production"),
            ("finishgoods.view_stock", "View FG Stock", "FinishGoods", "View finish goods inventory"),
            ("finishgoods.create_shipment", "Create Shipment", "FinishGoods", "Create shipping documents"),
            ("finishgoods.approve_shipment", "Approve Shipment", "FinishGoods", "Approve for shipping"),
            ("finishgoods.load_container", "Load Container", "FinishGoods", "Container loading operations"),
            ("finishgoods.print_docs", "Print Documents", "FinishGoods", "Print shipping documents"),
            ("finishgoods.track_delivery", "Track Delivery", "FinishGoods", "Track shipment status"),
            ("finishgoods.customer_portal", "Customer Portal", "FinishGoods", "Access customer portal"),
            
            # Reports Module (7 permissions)
            ("reports.view_production", "View Production Reports", "Reports", "Production performance reports"),
            ("reports.view_quality", "View Quality Reports", "Reports", "Quality metrics reports"),
            ("reports.view_inventory", "View Inventory Reports", "Reports", "Stock and inventory reports"),
            ("reports.view_financial", "View Financial Reports", "Reports", "Cost and financial reports"),
            ("reports.export_reports", "Export Reports", "Reports", "Export reports to Excel/PDF"),
            ("reports.schedule_reports", "Schedule Reports", "Reports", "Setup automated reports"),
            ("reports.custom_reports", "Custom Reports", "Reports", "Create custom report builders"),
            
            # Kanban Module (5 permissions)
            ("kanban.view_boards", "View Kanban Boards", "Kanban", "View kanban workflow boards"),
            ("kanban.create_cards", "Create Kanban Cards", "Kanban", "Create new kanban cards"),
            ("kanban.move_cards", "Move Kanban Cards", "Kanban", "Move cards between columns"),
            ("kanban.manage_rules", "Manage Kanban Rules", "Kanban", "Configure kanban automation"),
            ("kanban.digital_ekanban", "Digital E-Kanban", "Kanban", "Use digital kanban system"),
            
            # Barcode Module (5 permissions)
            ("barcode.scan", "Scan Barcode", "Barcode", "Scan barcodes with camera/scanner"),
            ("barcode.validate", "Validate Barcode", "Barcode", "Validate barcode before transaction"),
            ("barcode.generate", "Generate Barcode", "Barcode", "Generate new barcodes"),
            ("barcode.print", "Print Barcode", "Barcode", "Print barcode labels"),
            ("barcode.bulk_operations", "Bulk Barcode Operations", "Barcode", "Batch barcode operations"),
        ]
        
        try:
            # Insert all permissions
            insert_sql = text("""
                INSERT INTO permissions (code, name, module, description)
                VALUES (:code, :name, :module, :description)
                ON CONFLICT (code) DO NOTHING
            """)
            
            for code, name, module, description in permissions_data:
                self.db.execute(insert_sql, {
                    "code": code,
                    "name": name,
                    "module": module,
                    "description": description
                })
            
            self.db.commit()
            
            # Verify count
            count_sql = text("SELECT COUNT(*) FROM permissions")
            count = self.db.execute(count_sql).scalar()
            
            self.log(f"Seeded {count} permissions successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to seed permissions: {str(e)}", "ERROR")
            return False
    
    def map_roles_to_permissions(self) -> bool:
        """Step 3: Map existing RBAC roles to PBAC permissions"""
        self.log("Mapping roles to permissions...", "INFO")
        
        # Role-to-Permission mapping (preserves existing RBAC access)
        role_permission_map: Dict[UserRole, List[str]] = {
            # Level 0: Full system access
            UserRole.DEVELOPER: ["*"],  # All permissions
            
            # Level 1: Administrative access
            UserRole.SUPERADMIN: ["*"],  # All permissions
            
            # Level 2: Management access
            UserRole.MANAGER: [
                "ppic.approve_mo",
                "purchasing.approve_po",
                "warehouse.approve_adjustment",
                "admin.view_audit_logs",
                "reports.*",
                "qc.view_reports",
                "finishgoods.*",
            ],
            
            UserRole.FINANCE_MANAGER: [
                "reports.view_financial",
                "reports.view_inventory",
                "reports.export_reports",
                "admin.view_audit_logs",
                "purchasing.view_po",
                "warehouse.view_stock",
            ],
            
            # Level 3: System administrators
            UserRole.ADMIN: [
                "admin.*",
                "purchasing.*",
                "warehouse.*",
                "ppic.*",
                "reports.*",
                "qc.*",
                "barcode.*",
                "kanban.*",
            ],
            
            # Level 4: Department managers
            UserRole.PPIC_MANAGER: [
                "ppic.create_mo",
                "ppic.edit_mo",
                "ppic.approve_mo",
                "ppic.explode_bom",
                "ppic.plan_production",
                "ppic.allocate_materials",
                "ppic.view_capacity",
                "ppic.manage_bom",
                "reports.view_production",
            ],
            
            UserRole.PPIC_ADMIN: [
                "ppic.create_mo",
                "ppic.edit_mo",
                "ppic.explode_bom",
                "ppic.allocate_materials",
                "ppic.view_mo",
            ],
            
            UserRole.SPV_CUTTING: [
                "cutting.*",
                "reports.view_production",
            ],
            
            UserRole.SPV_SEWING: [
                "sewing.*",
                "reports.view_production",
            ],
            
            UserRole.SPV_FINISHING: [
                "finishing.*",
                "reports.view_production",
            ],
            
            UserRole.WAREHOUSE_ADMIN: [
                "warehouse.*",
                "barcode.*",
                "reports.view_inventory",
            ],
            
            UserRole.QC_LAB: [
                "qc.*",
                "reports.view_quality",
            ],
            
            UserRole.PURCHASING_HEAD: [
                "purchasing.create_po",
                "purchasing.edit_po",
                "purchasing.approve_po",
                "purchasing.send_po",
                "purchasing.view_po",
                "purchasing.vendor_management",
                "reports.view_financial",
            ],
            
            UserRole.PURCHASING: [
                "purchasing.create_po",
                "purchasing.edit_po",
                "purchasing.view_po",
            ],
            
            # Level 5: Operators
            UserRole.OPERATOR_CUT: [
                "cutting.execute",
                "cutting.view_work_order",
                "cutting.create_transfer",
                "cutting.report_shortage",
                "cutting.report_surplus",
                "cutting.print_transfer_slip",
                "barcode.scan",
            ],
            
            UserRole.OPERATOR_EMBRO: [
                "embroidery.execute",
                "embroidery.view_work_order",
                "embroidery.create_transfer",
                "barcode.scan",
            ],
            
            UserRole.OPERATOR_SEW: [
                "sewing.execute",
                "sewing.view_work_order",
                "sewing.create_transfer",
                "sewing.segregate_defects",
                "sewing.quality_inline",
                "barcode.scan",
            ],
            
            UserRole.OPERATOR_FINISH: [
                "finishing.execute",
                "finishing.stuffing",
                "finishing.closing",
                "finishing.view_work_order",
                "finishing.create_transfer",
                "barcode.scan",
            ],
            
            UserRole.OPERATOR_PACK: [
                "packing.execute",
                "packing.view_work_order",
                "packing.create_carton",
                "packing.print_labels",
                "packing.transfer_to_fg",
                "kanban.view_boards",
                "kanban.move_cards",
                "barcode.scan",
            ],
            
            UserRole.QC_INSPECTOR: [
                "qc.inline_inspection",
                "qc.final_inspection",
                "qc.view_inspections",
                "qc.upload_evidence",
            ],
            
            UserRole.WAREHOUSE_OP: [
                "warehouse.receive_goods",
                "warehouse.view_stock",
                "warehouse.transfer_stock",
                "warehouse.barcode_scan",
                "barcode.scan",
                "barcode.validate",
            ],
            
            UserRole.SECURITY: [
                "warehouse.view_stock",
                "finishgoods.view_stock",
                "finishgoods.track_delivery",
            ],
        }
        
        try:
            # Get permission IDs for mapping
            permissions_sql = text("SELECT id, code FROM permissions")
            permissions_result = self.db.execute(permissions_sql).fetchall()
            permission_map = {row[1]: row[0] for row in permissions_result}
            
            insert_sql = text("""
                INSERT INTO role_permissions (role, permission_id)
                VALUES (:role, :permission_id)
                ON CONFLICT (role, permission_id) DO NOTHING
            """)
            
            total_mappings = 0
            
            for role, permission_patterns in role_permission_map.items():
                for pattern in permission_patterns:
                    if pattern == "*":
                        # Grant all permissions
                        for perm_id in permission_map.values():
                            self.db.execute(insert_sql, {
                                "role": role.value,
                                "permission_id": perm_id
                            })
                            total_mappings += 1
                    elif pattern.endswith(".*"):
                        # Grant all permissions in module
                        module = pattern.replace(".*", "")
                        for code, perm_id in permission_map.items():
                            if code.startswith(f"{module}."):
                                self.db.execute(insert_sql, {
                                    "role": role.value,
                                    "permission_id": perm_id
                                })
                                total_mappings += 1
                    else:
                        # Grant specific permission
                        if pattern in permission_map:
                            self.db.execute(insert_sql, {
                                "role": role.value,
                                "permission_id": permission_map[pattern]
                            })
                            total_mappings += 1
            
            self.db.commit()
            
            self.log(f"Created {total_mappings} role-permission mappings", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to map roles to permissions: {str(e)}", "ERROR")
            return False
    
    def validate_migration(self) -> Tuple[bool, List[str]]:
        """Step 4: Validate migration success"""
        self.log("Validating migration...", "INFO")
        
        errors = []
        
        try:
            # Check 1: All users still have access
            users_sql = text("""
                SELECT u.id, u.username, u.role, COUNT(rp.id) as perm_count
                FROM users u
                LEFT JOIN role_permissions rp ON rp.role = u.role
                GROUP BY u.id, u.username, u.role
            """)
            users_result = self.db.execute(users_sql).fetchall()
            
            for user_id, username, role, perm_count in users_result:
                if perm_count == 0:
                    errors.append(f"User {username} ({role}) has NO permissions!")
            
            # Check 2: Permission count matches expected
            perm_count_sql = text("SELECT COUNT(*) FROM permissions")
            perm_count = self.db.execute(perm_count_sql).scalar()
            
            if perm_count < 100:
                errors.append(f"Only {perm_count} permissions found (expected 100+)")
            
            # Check 3: All roles mapped
            role_perm_count_sql = text("SELECT COUNT(*) FROM role_permissions")
            role_perm_count = self.db.execute(role_perm_count_sql).scalar()
            
            if role_perm_count < 100:
                errors.append(f"Only {role_perm_count} role-permission mappings (expected 100+)")
            
            # Check 4: Tables created successfully
            tables_sql = text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('permissions', 'role_permissions', 'user_custom_permissions')
            """)
            tables = self.db.execute(tables_sql).fetchall()
            
            if len(tables) != 3:
                errors.append(f"Only {len(tables)}/3 PBAC tables created")
            
            if errors:
                self.log(f"Validation FAILED with {len(errors)} errors", "ERROR")
                for error in errors:
                    self.log(f"  - {error}", "ERROR")
                return False, errors
            else:
                self.log("Migration validation PASSED", "SUCCESS")
                return True, []
                
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
    
    def mark_completed(self, success: bool, error_message: str = None):
        """Mark migration as completed"""
        try:
            update_sql = text("""
                UPDATE pbac_migrations
                SET completed_at = NOW(),
                    status = :status,
                    error_message = :error_message
                WHERE migration_id = :migration_id
            """)
            
            self.db.execute(update_sql, {
                "status": "SUCCESS" if success else "FAILED",
                "error_message": error_message,
                "migration_id": self.migration_id
            })
            self.db.commit()
            
        except Exception as e:
            self.log(f"Failed to mark migration status: {str(e)}", "ERROR")
    
    def rollback(self):
        """Rollback migration on failure"""
        self.log("ROLLBACK: Dropping PBAC tables...", "ERROR")
        
        try:
            rollback_sql = text("""
                DROP TABLE IF EXISTS user_custom_permissions CASCADE;
                DROP TABLE IF EXISTS role_permissions CASCADE;
                DROP TABLE IF EXISTS permissions CASCADE;
                DROP TABLE IF EXISTS pbac_migrations CASCADE;
            """)
            
            self.db.execute(rollback_sql)
            self.db.commit()
            
            self.log("Rollback complete - system reverted to RBAC", "SUCCESS")
            
        except Exception as e:
            self.log(f"CRITICAL: Rollback failed: {str(e)}", "ERROR")
            self.log("Manual intervention required! Contact DBA immediately.", "ERROR")


def main():
    """Execute migration"""
    print("="*70)
    print("RBAC → PBAC MIGRATION")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db = SessionLocal()
    migration = PBACMigration(db)
    
    try:
        # Step 1: Create tables
        if not migration.create_permissions_tables():
            migration.rollback()
            sys.exit(1)
        
        print()
        
        # Step 2: Seed permissions
        if not migration.seed_permissions():
            migration.rollback()
            sys.exit(1)
        
        print()
        
        # Step 3: Map roles to permissions
        if not migration.map_roles_to_permissions():
            migration.rollback()
            sys.exit(1)
        
        print()
        
        # Step 4: Validate
        success, errors = migration.validate_migration()
        if not success:
            migration.mark_completed(False, "; ".join(errors))
            migration.rollback()
            sys.exit(1)
        
        # Mark as completed
        migration.mark_completed(True)
        
        print()
        print("="*70)
        print("✅ MIGRATION COMPLETE")
        print("="*70)
        print()
        print("Next steps:")
        print("1. Test all endpoints with different user roles")
        print("2. Monitor application logs for permission errors")
        print("3. Update API endpoints to use require_permission()")
        print("4. Conduct User Acceptance Testing (UAT)")
        print()
        
    except Exception as e:
        print()
        print(f"❌ MIGRATION FAILED: {str(e)}")
        migration.mark_completed(False, str(e))
        migration.rollback()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
