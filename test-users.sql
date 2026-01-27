-- Test Users for ERP System
-- Password: password123
-- Hash: $2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2

DELETE FROM users WHERE username IN ('developer', 'admin', 'operator_cut', 'qc_lab');

INSERT INTO users (username, email, hashed_password, full_name, role, is_active, created_at)
VALUES
  ('developer', 'developer@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'System Developer', 'DEVELOPER', true, NOW()),
  ('admin', 'admin@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'System Administrator', 'ADMIN', true, NOW()),
  ('operator_cut', 'operator.cutting@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'Operator Cutting', 'OPERATOR_CUT', true, NOW()),
  ('qc_lab', 'qc.lab@qutykarunia.com', '$2b$12$c625pblE8g2HK67.P1ooCevVT2h79OekfZCxJvHeKGrrzPF9meAW2', 'QC Laboratory', 'QC_LAB', true, NOW());

SELECT username, email, role, is_active FROM users ORDER BY username;
