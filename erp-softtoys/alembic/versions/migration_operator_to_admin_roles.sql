-- Migration: Replace OPERATOR_* roles with ADMIN_* roles
-- Date: 2026-02-20
-- Purpose: Change operator roles to department admin roles for better access control

-- Step 1: Update UserRole ENUM type
ALTER TYPE userrole RENAME VALUE 'Operator Cutting' TO 'Admin Cutting';
ALTER TYPE userrole RENAME VALUE 'Operator Embroidery' TO 'Admin Embroidery';
ALTER TYPE userrole RENAME VALUE 'Operator Sewing' TO 'Admin Sewing';
ALTER TYPE userrole RENAME VALUE 'Operator Finishing' TO 'Admin Finishing';
ALTER TYPE userrole RENAME VALUE 'Operator Packing' TO 'Admin Packing';

-- Step 2: Update existing users with operator roles
UPDATE users SET role = 'Admin Cutting' WHERE role = 'Operator Cutting';
UPDATE users SET role = 'Admin Embroidery' WHERE role = 'Operator Embroidery';
UPDATE users SET role = 'Admin Sewing' WHERE role = 'Operator Sewing';
UPDATE users SET role = 'Admin Finishing' WHERE role = 'Operator Finishing';
UPDATE users SET role = 'Admin Packing' WHERE role = 'Admin Packing';

-- Step 3: Update usernames if needed (optional)
UPDATE users SET username = 'admin_cutting' WHERE username = 'operator_cut';
UPDATE users SET username = 'admin_embroidery' WHERE username = 'operator_embro';
UPDATE users SET username = 'admin_sewing' WHERE username = 'operator_sew';
UPDATE users SET username = 'admin_finishing' WHERE username = 'operator_finish';
UPDATE users SET username = 'admin_packing' WHERE username = 'operator_pack';

-- Step 4: Update email addresses
UPDATE users SET email = 'admin.cutting@qutykarunia.com' WHERE username = 'admin_cutting';
UPDATE users SET email = 'admin.embroidery@qutykarunia.com' WHERE username = 'admin_embroidery';
UPDATE users SET email = 'admin.sewing@qutykarunia.com' WHERE username = 'admin_sewing';
UPDATE users SET email = 'admin.finishing@qutykarunia.com' WHERE username = 'admin_finishing';
UPDATE users SET email = 'admin.packing@qutykarunia.com' WHERE username = 'admin_packing';

-- Step 5: Update full_name
UPDATE users SET full_name = 'Admin Cutting' WHERE username = 'admin_cutting';
UPDATE users SET full_name = 'Admin Embroidery' WHERE username = 'admin_embroidery';
UPDATE users SET full_name = 'Admin Sewing' WHERE username = 'admin_sewing';
UPDATE users SET full_name = 'Admin Finishing' WHERE username = 'admin_finishing';
UPDATE users SET full_name = 'Admin Packing' WHERE username = 'admin_packing';

-- Verification query
SELECT username, email, full_name, role 
FROM users 
WHERE role IN ('Admin Cutting', 'Admin Embroidery', 'Admin Sewing', 'Admin Finishing', 'Admin Packing')
ORDER BY role;
