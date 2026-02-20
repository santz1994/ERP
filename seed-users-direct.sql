-- Seed 22 Users for ERP System
-- Direct SQL insert to bypass Python bcrypt compatibility issues
-- Enum values must be UPPERCASE with underscores: DEVELOPER, SUPERADMIN, etc.

DELETE FROM users WHERE username IN ('developer', 'superadmin', 'manager', 'finance_mgr', 'admin', 
  'ppic_mgr', 'ppic_admin', 'spv_cutting', 'spv_sewing', 'spv_finishing', 'wh_admin', 'qc_lab',
  'purchasing_head', 'purchasing', 'admin_cutting', 'admin_embroidery', 'admin_sewing', 
  'admin_finishing', 'admin_packing', 'qc_inspector', 'wh_operator', 'security');

-- Level 0: System Development
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('developer', 'developer@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'System Developer', 'DEVELOPER'::userrole, true, true, NOW());

-- Level 1: System Administration
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('superadmin', 'superadmin@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Super Administrator', 'SUPERADMIN'::userrole, true, true, NOW());

-- Level 2: Top Management
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('manager', 'manager@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'General Manager', 'MANAGER'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('finance_mgr', 'finance.manager@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Finance Manager', 'FINANCE_MANAGER'::userrole, true, true, NOW());

-- Level 3: System Admin
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('admin', 'admin@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'System Administrator', 'ADMIN'::userrole, true, true, NOW());

-- Level 4: Department Management
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('ppic_mgr', 'ppic.manager@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'PPIC Manager', 'PPIC_MANAGER'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('ppic_admin', 'ppic.admin@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'PPIC Admin', 'PPIC_ADMIN'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('spv_cutting', 'spv.cutting@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Supervisor Cutting', 'SPV_CUTTING'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('spv_sewing', 'spv.sewing@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Supervisor Sewing', 'SPV_SEWING'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('spv_finishing', 'spv.finishing@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Supervisor Finishing', 'SPV_FINISHING'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('wh_admin', 'warehouse.admin@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Warehouse Admin', 'WAREHOUSE_ADMIN'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('qc_lab', 'qc.lab@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'QC Laboratory', 'QC_LAB'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('purchasing_head', 'purchasing.head@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Purchasing Head', 'PURCHASING_HEAD'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('purchasing', 'purchasing@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Purchasing Officer', 'PURCHASING'::userrole, true, true, NOW());

-- Level 5: Department Administration
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('admin_cutting', 'admin.cutting@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Admin Cutting', 'ADMIN_CUTTING'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('admin_embroidery', 'admin.embroidery@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Admin Embroidery', 'ADMIN_EMBROIDERY'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('admin_sewing', 'admin.sewing@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Admin Sewing', 'ADMIN_SEWING'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('admin_finishing', 'admin.finishing@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Admin Finishing', 'ADMIN_FINISHING'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('admin_packing', 'admin.packing@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Admin Packing', 'ADMIN_PACKING'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('qc_inspector', 'qc.inspector@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'QC Inspector', 'QC_INSPECTOR'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('wh_operator', 'warehouse.operator@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Warehouse Operator', 'WAREHOUSE_OP'::userrole, true, true, NOW());

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, created_at)
VALUES ('security', 'security@qutykarunia.com', '$2b$10$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890', 'Security Guard', 'SECURITY'::userrole, true, true, NOW());

-- Verify insertion
SELECT COUNT(*) as total_users, COUNT(DISTINCT role) as unique_roles FROM users;
SELECT '✅ SEEDED:' as status;
SELECT username, role FROM users ORDER BY role;
