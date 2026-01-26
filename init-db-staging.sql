-- ERP2026 Database Initialization Script
-- For testing and staging environments
-- Created: 2026-01-26

-- ============================================================================
-- CREATE ROLES
-- ============================================================================

-- Create application user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'erp_staging_user') THEN
        CREATE ROLE erp_staging_user WITH LOGIN PASSWORD 'erp_staging_pass';
    END IF;
END
$$;

-- ============================================================================
-- SCHEMA SETUP
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS erp;
SET search_path TO erp, public;

-- ============================================================================
-- USER ROLES
-- ============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(50) NOT NULL DEFAULT 'OPERATOR',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- ARTICLES & MATERIALS
-- ============================================================================

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    unit VARCHAR(20) DEFAULT 'PCS',
    production_target_monthly INT DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_articles_code ON articles(code);

CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    unit VARCHAR(20) DEFAULT 'KG',
    price DECIMAL(12, 2),
    supplier_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materials_code ON materials(code);

-- ============================================================================
-- PRODUCTION TRACKING
-- ============================================================================

CREATE TABLE production_lines (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE daily_production (
    id SERIAL PRIMARY KEY,
    line_id INT REFERENCES production_lines(id),
    article_id INT REFERENCES articles(id),
    production_date DATE NOT NULL,
    quantity INT NOT NULL,
    approval_status VARCHAR(50) DEFAULT 'PENDING',
    approved_by INT REFERENCES users(id),
    approved_at TIMESTAMP,
    cumulative_quantity INT,
    remarks TEXT,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(line_id, article_id, production_date)
);

CREATE INDEX idx_daily_production_date ON daily_production(production_date);
CREATE INDEX idx_daily_production_status ON daily_production(approval_status);
CREATE INDEX idx_daily_production_article ON daily_production(article_id);

-- ============================================================================
-- APPROVAL WORKFLOW
-- ============================================================================

CREATE TABLE approvals (
    id SERIAL PRIMARY KEY,
    production_id INT REFERENCES daily_production(id),
    status VARCHAR(50) DEFAULT 'PENDING',
    requested_by INT REFERENCES users(id),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INT REFERENCES users(id),
    approved_at TIMESTAMP,
    rejected_by INT REFERENCES users(id),
    rejected_at TIMESTAMP,
    rejection_reason TEXT,
    remarks TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_approvals_production_id ON approvals(production_id);

CREATE TABLE approval_audit (
    id SERIAL PRIMARY KEY,
    approval_id INT REFERENCES approvals(id),
    action VARCHAR(50),
    user_id INT REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- ============================================================================
-- BARCODE MANAGEMENT
-- ============================================================================

CREATE TABLE barcodes (
    id SERIAL PRIMARY KEY,
    barcode_value VARCHAR(500) UNIQUE NOT NULL,
    carton_id VARCHAR(100),
    article_id INT REFERENCES articles(id),
    quantity INT,
    scanned_by INT REFERENCES users(id),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    production_id INT REFERENCES daily_production(id),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_barcodes_value ON barcodes(barcode_value);
CREATE INDEX idx_barcodes_carton ON barcodes(carton_id);

-- ============================================================================
-- MATERIAL DEBT TRACKING
-- ============================================================================

CREATE TABLE material_debt (
    id SERIAL PRIMARY KEY,
    material_id INT REFERENCES materials(id),
    creditor VARCHAR(200),
    quantity INT NOT NULL,
    price DECIMAL(12, 2),
    amount DECIMAL(12, 2),
    created_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    settled_date DATE,
    status VARCHAR(50) DEFAULT 'OUTSTANDING',
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_debt_status ON material_debt(status);
CREATE INDEX idx_material_debt_creditor ON material_debt(creditor);
CREATE INDEX idx_material_debt_due_date ON material_debt(due_date);

CREATE TABLE debt_settlement (
    id SERIAL PRIMARY KEY,
    debt_id INT REFERENCES material_debt(id),
    settlement_amount DECIMAL(12, 2),
    settlement_date DATE DEFAULT CURRENT_DATE,
    receipt_number VARCHAR(100),
    notes TEXT,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUDIT & LOGGING
-- ============================================================================

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100),
    entity_id INT,
    action VARCHAR(50),
    user_id INT REFERENCES users(id),
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50)
);

CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);

-- ============================================================================
-- TEST DATA
-- ============================================================================

-- Insert test users
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('operator1', 'operator1@company.com', '$2b$12$...', 'Operator One', 'OPERATOR'),
('supervisor1', 'supervisor1@company.com', '$2b$12$...', 'Supervisor One', 'SUPERVISOR'),
('manager1', 'manager1@company.com', '$2b$12$...', 'Manager One', 'MANAGER'),
('admin1', 'admin1@company.com', '$2b$12$...', 'Admin One', 'ADMIN');

-- Insert test articles
INSERT INTO articles (code, name, description, production_target_monthly) VALUES
('ARTICLE001', 'Soft Toy - Bear', 'Plush teddy bear', 500),
('ARTICLE002', 'Soft Toy - Cat', 'Plush cat toy', 450),
('ARTICLE003', 'Soft Toy - Dog', 'Plush dog toy', 600),
('ARTICLE004', 'Soft Toy - Bunny', 'Plush bunny toy', 400),
('ARTICLE005', 'Soft Toy - Monkey', 'Plush monkey toy', 350);

-- Insert test materials
INSERT INTO materials (code, name, unit, price, supplier_id) VALUES
('MAT001', 'Polyester Fabric', 'KG', 50.00, NULL),
('MAT002', 'Polyester Filling', 'KG', 30.00, NULL),
('MAT003', 'Thread - Black', 'SPOOL', 5.00, NULL),
('MAT004', 'Eyes - Button', 'BOX', 25.00, NULL),
('MAT005', 'Nose - Plastic', 'BOX', 15.00, NULL);

-- Insert test production lines
INSERT INTO production_lines (code, name, status) VALUES
('LINE001', 'Cutting Line 1', 'ACTIVE'),
('LINE002', 'Stitching Line 1', 'ACTIVE'),
('LINE003', 'Filling Line 1', 'ACTIVE'),
('LINE004', 'Assembly Line 1', 'ACTIVE'),
('LINE005', 'Quality Check Line', 'ACTIVE');

-- Insert sample daily production
INSERT INTO daily_production (line_id, article_id, production_date, quantity, approval_status, created_by) VALUES
(1, 1, CURRENT_DATE - INTERVAL '5 days', 100, 'APPROVED', 1),
(1, 1, CURRENT_DATE - INTERVAL '4 days', 120, 'APPROVED', 1),
(1, 1, CURRENT_DATE - INTERVAL '3 days', 110, 'APPROVED', 1),
(2, 2, CURRENT_DATE - INTERVAL '2 days', 95, 'PENDING', 1),
(3, 3, CURRENT_DATE - INTERVAL '1 days', 105, 'PENDING', 1),
(4, 1, CURRENT_DATE, 90, 'PENDING', 1);

-- Insert sample material debt
INSERT INTO material_debt (material_id, creditor, quantity, price, amount, due_date, status, created_by) VALUES
(1, 'SUPPLIER001', 500, 50.00, 25000.00, CURRENT_DATE + INTERVAL '30 days', 'OUTSTANDING', 1),
(2, 'SUPPLIER002', 1000, 30.00, 30000.00, CURRENT_DATE + INTERVAL '45 days', 'OUTSTANDING', 1),
(3, 'SUPPLIER003', 100, 5.00, 500.00, CURRENT_DATE - INTERVAL '5 days', 'OUTSTANDING', 1),
(4, 'SUPPLIER004', 50, 25.00, 1250.00, CURRENT_DATE + INTERVAL '60 days', 'OUTSTANDING', 1);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update cumulative production on daily_production insert
CREATE OR REPLACE FUNCTION update_cumulative_production()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE daily_production
    SET cumulative_quantity = (
        SELECT SUM(quantity)
        FROM daily_production
        WHERE article_id = NEW.article_id
        AND production_date <= NEW.production_date
    )
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cumulative_production
AFTER INSERT ON daily_production
FOR EACH ROW EXECUTE FUNCTION update_cumulative_production();

-- Update modified timestamp
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_daily_production_timestamp
BEFORE UPDATE ON daily_production
FOR EACH ROW EXECUTE FUNCTION update_modified_timestamp();

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

CREATE VIEW v_daily_summary AS
SELECT
    dp.production_date,
    a.code as article_code,
    a.name as article_name,
    SUM(dp.quantity) as total_quantity,
    COUNT(*) as record_count,
    COUNT(CASE WHEN dp.approval_status = 'APPROVED' THEN 1 END) as approved_count,
    COUNT(CASE WHEN dp.approval_status = 'PENDING' THEN 1 END) as pending_count
FROM daily_production dp
JOIN articles a ON dp.article_id = a.id
GROUP BY dp.production_date, a.code, a.name;

CREATE VIEW v_outstanding_debt AS
SELECT
    md.creditor,
    SUM(md.amount) as total_amount,
    COUNT(*) as record_count,
    MIN(md.due_date) as earliest_due_date,
    MAX(md.due_date) as latest_due_date
FROM material_debt md
WHERE md.status = 'OUTSTANDING'
GROUP BY md.creditor;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE daily_production IS 'Daily production tracking records';
COMMENT ON TABLE approvals IS 'Approval workflow for production records';
COMMENT ON TABLE material_debt IS 'Material debt tracking and reconciliation';
COMMENT ON TABLE barcodes IS 'Barcode scanning and tracking';

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA erp TO erp_staging_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA erp TO erp_staging_user;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
