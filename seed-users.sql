-- Seed test users for ERP2026 Staging
-- Password hashing using bcrypt (cost=12)
-- All users have password: "password123"
-- Testing: UAC (User Access Control), RBAC (Role-Based Access Control), PBAC (Permission-Based Access Control)

SET search_path TO erp, public;

-- Insert comprehensive test users for all 22 roles
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, created_at)
VALUES
  -- Level 0: System Development & Protection (UAC - User Access Control)
  ('developer', 'developer@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'System Developer', 'Developer', true, NOW()),

  -- Level 1: System Administration (UAC/RBAC - Super Admin)
  ('superadmin', 'superadmin@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Super Administrator', 'Superadmin', true, NOW()),

  -- Level 2: Top Management (RBAC - Approval Authority)
  ('manager', 'manager@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'General Manager', 'Manager', true, NOW()),
  ('finance_mgr', 'finance.manager@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Finance Manager', 'Finance Manager', true, NOW()),

  -- Level 3: System Admin (RBAC - Admin)
  ('admin', 'admin@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'System Administrator', 'Admin', true, NOW()),

  -- Level 4: Department Management (RBAC/PBAC - Department Managers)
  ('ppic_mgr', 'ppic.manager@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'PPIC Manager', 'PPIC Manager', true, NOW()),
  ('ppic_admin', 'ppic.admin@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'PPIC Admin', 'PPIC Admin', true, NOW()),
  ('spv_cutting', 'spv.cutting@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Supervisor Cutting', 'SPV Cutting', true, NOW()),
  ('spv_sewing', 'spv.sewing@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Supervisor Sewing', 'SPV Sewing', true, NOW()),
  ('spv_finishing', 'spv.finishing@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Supervisor Finishing', 'SPV Finishing', true, NOW()),
  ('wh_admin', 'warehouse.admin@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Warehouse Admin', 'Warehouse Admin', true, NOW()),
  ('qc_lab', 'qc.lab@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'QC Laboratory', 'QC Lab', true, NOW()),
  ('purchasing_head', 'purchasing.head@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Purchasing Head', 'Purchasing Head', true, NOW()),
  ('purchasing', 'purchasing@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Purchasing Officer', 'Purchasing', true, NOW()),

  -- Level 5: Department Administration (PBAC - Permission-Based Operations)
  ('admin_cutting', 'admin.cutting@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Admin Cutting', 'Admin Cutting', true, NOW()),
  ('admin_embroidery', 'admin.embroidery@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Admin Embroidery', 'Admin Embroidery', true, NOW()),
  ('admin_sewing', 'admin.sewing@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Admin Sewing', 'Admin Sewing', true, NOW()),
  ('admin_finishing', 'admin.finishing@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Admin Finishing', 'Admin Finishing', true, NOW()),
  ('admin_packing', 'admin.packing@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Admin Packing', 'Admin Packing', true, NOW()),
  ('qc_inspector', 'qc.inspector@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'QC Inspector', 'QC Inspector', true, NOW()),
  ('wh_operator', 'warehouse.operator@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Warehouse Operator', 'Warehouse Operator', true, NOW()),
  ('security', 'security@qutykarunia.com', '$2b$12$z0xaLPyH3qChVQJ9OmjYZe1sLbg9kHUlHK8J5L3qK4l8Z8K0l1L3y', 'Security Guard', 'Security', true, NOW())
ON CONFLICT (username) DO NOTHING;

-- Verify seed - show UAC/RBAC/PBAC breakdown
SELECT 'Total Users' as category, COUNT(*) as count FROM users
UNION ALL
SELECT 'By Role', COUNT(DISTINCT role) FROM users
UNION ALL
SELECT 'Active Users', COUNT(*) FROM users WHERE is_active = true;
