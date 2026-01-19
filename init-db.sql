-- Initialize PostgreSQL database with production-ready schema
-- Run only once during container startup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Set timezone to WIB (UTC+7)
SET timezone = 'Asia/Jakarta';

-- Create enum types
CREATE TYPE user_role AS ENUM (
    'admin',
    'ppic_manager',
    'ppic_staff',
    'spv_cutting',
    'spv_embroidery',
    'spv_sewing',
    'spv_finishing',
    'spv_packing',
    'operator_cutting',
    'operator_embroidery',
    'operator_sewing',
    'operator_finishing',
    'operator_packing',
    'qc_inspector',
    'warehouse_admin',
    'purchasing'
);

CREATE TYPE product_type AS ENUM (
    'Raw Material',
    'WIP',
    'Finish Good',
    'Service'
);

CREATE TYPE alert_severity AS ENUM (
    'INFO',
    'WARNING',
    'CRITICAL'
);

CREATE TYPE department_type AS ENUM (
    'Warehouse',
    'Cutting',
    'Embroidery',
    'Sewing',
    'Finishing',
    'Packing',
    'FinishGood'
);

-- Create indexes for performance
CREATE INDEX idx_products_code ON products(code);
CREATE INDEX idx_products_type ON products(type);
CREATE INDEX idx_manufacturing_orders_batch ON manufacturing_orders(batch_number);
CREATE INDEX idx_work_orders_department ON work_orders(department);
CREATE INDEX idx_work_orders_status ON work_orders(status);
CREATE INDEX idx_transfer_logs_from_dept ON transfer_logs(from_dept);
CREATE INDEX idx_transfer_logs_to_dept ON transfer_logs(to_dept);
CREATE INDEX idx_stock_quants_product ON stock_quants(product_id);
CREATE INDEX idx_stock_quants_location ON stock_quants(location_id);
CREATE INDEX idx_qc_tests_batch ON qc_lab_tests(batch_number);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE erp_quty_karunia TO postgres;
