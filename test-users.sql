-- Test Users for ERP System
-- Password: password123
-- Hash: $2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2

DELETE FROM users WHERE username IN ('developer', 'admin', 'admin_cutting', 'qc_lab');

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, created_at)
VALUES
  ('developer', 'developer@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'System Developer', 'DEVELOPER', true, NOW()),
  ('admin', 'admin@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'System Administrator', 'ADMIN', true, NOW()),
  ('admin_cutting', 'admin.cutting@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'Admin Cutting', 'ADMIN_CUTTING', true, NOW()),
  ('qc_lab', 'qc.lab@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'QC Laboratory', 'QC_LAB', true, NOW());

SELECT username, email, role, is_active FROM users ORDER BY username;
