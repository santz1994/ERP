-- ============================================================================
-- Quty Karunia ERP - Database Optimization Script
-- Creates indexes and configures production settings
-- Run this after all migrations are complete
-- ============================================================================

-- ============================================================================
-- 1. PERFORMANCE INDEXES - Critical Queries
-- ============================================================================

-- Transfer Protocol Indexes (QT-09)
CREATE INDEX IF NOT EXISTS idx_transfer_logs_status_created 
    ON transfer_logs(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transfer_logs_from_to_dept 
    ON transfer_logs(from_dept, to_dept, status);

CREATE INDEX IF NOT EXISTS idx_line_occupancy_dept_article 
    ON line_occupancy(to_dept, article_id, is_clear);

-- Manufacturing Order Indexes
CREATE INDEX IF NOT EXISTS idx_manufacturing_orders_state_created 
    ON manufacturing_orders(state, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_manufacturing_orders_so_line_id 
    ON manufacturing_orders(so_line_id);

-- Work Order Indexes
CREATE INDEX IF NOT EXISTS idx_work_orders_department_status 
    ON work_orders(department, status);

CREATE INDEX IF NOT EXISTS idx_work_orders_mo_id_department 
    ON work_orders(mo_id, department);

-- Stock Management Indexes
CREATE INDEX IF NOT EXISTS idx_stock_quants_product_location 
    ON stock_quants(product_id, location_id);

CREATE INDEX IF NOT EXISTS idx_stock_quants_product_qty 
    ON stock_quants(product_id, qty_on_hand) 
    WHERE qty_on_hand > 0;

CREATE INDEX IF NOT EXISTS idx_stock_moves_product_location_date 
    ON stock_moves(product_id, location_id_from, location_id_to, date);

-- Quality Control Indexes
CREATE INDEX IF NOT EXISTS idx_qc_inspections_batch_created 
    ON qc_inspections(batch_number, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_qc_inspections_type_status 
    ON qc_inspections(type, status);

CREATE INDEX IF NOT EXISTS idx_qc_lab_tests_batch_type 
    ON qc_lab_tests(batch_number, test_type);

-- Metal Detector Specific Index (Critical QC)
CREATE INDEX IF NOT EXISTS idx_metal_detector_results 
    ON qc_lab_tests(test_type, test_result, created_at DESC) 
    WHERE test_type = 'Metal Detector';

-- BOM Indexes
CREATE INDEX IF NOT EXISTS idx_bom_headers_product_active 
    ON bom_headers(product_id, is_active);

CREATE INDEX IF NOT EXISTS idx_bom_details_bom_header_id 
    ON bom_details(bom_header_id);

-- User & Authentication Indexes
CREATE INDEX IF NOT EXISTS idx_users_email_active 
    ON users(email) 
    WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_users_role_department 
    ON users(role, department) 
    WHERE is_active = true;

-- Product Indexes
CREATE INDEX IF NOT EXISTS idx_products_code 
    ON products(code);

CREATE INDEX IF NOT EXISTS idx_products_type_active 
    ON products(type) 
    WHERE is_active = true;

-- Sales Order Indexes
CREATE INDEX IF NOT EXISTS idx_sales_orders_po_number 
    ON sales_orders(po_number_buyer);

CREATE INDEX IF NOT EXISTS idx_sales_orders_delivery_week 
    ON sales_orders(delivery_week, destination);

-- ============================================================================
-- 2. PARTIAL INDEXES - For Performance on Large Tables
-- ============================================================================

-- Active manufacturing orders only
CREATE INDEX IF NOT EXISTS idx_manufacturing_orders_active 
    ON manufacturing_orders(id, state) 
    WHERE state IN ('Draft', 'In Progress');

-- Active work orders only
CREATE INDEX IF NOT EXISTS idx_work_orders_active 
    ON work_orders(id, status) 
    WHERE status IN ('Pending', 'Running');

-- Recent transfers (last 30 days)
CREATE INDEX IF NOT EXISTS idx_transfer_logs_recent 
    ON transfer_logs(id, created_at) 
    WHERE created_at > NOW() - INTERVAL '30 days';

-- Failed QC inspections only
CREATE INDEX IF NOT EXISTS idx_qc_inspections_failed 
    ON qc_inspections(id, batch_number) 
    WHERE status = 'Fail';

-- ============================================================================
-- 3. COMPOSITE INDEXES - For Complex Queries
-- ============================================================================

-- Transfer workflow queries
CREATE INDEX IF NOT EXISTS idx_transfer_workflow 
    ON transfer_logs(from_dept, to_dept, status, created_at DESC) 
    WHERE status != 'CANCELLED';

-- Production line status queries
CREATE INDEX IF NOT EXISTS idx_work_order_timeline 
    ON work_orders(department, status, start_time, end_time) 
    WHERE status IN ('Pending', 'Running');

-- Stock movement queries
CREATE INDEX IF NOT EXISTS idx_stock_fifo 
    ON stock_moves(product_id, location_id_from, date) 
    WHERE state = 'Done';

-- QC trending queries
CREATE INDEX IF NOT EXISTS idx_qc_trend_analysis 
    ON qc_inspections(work_order_id, status, created_at DESC) 
    WHERE created_at > NOW() - INTERVAL '90 days';

-- ============================================================================
-- 4. ANALYZE & VACUUM
-- ============================================================================

-- Analyze all tables for query planner optimization
ANALYZE;

-- ============================================================================
-- 5. CONNECTION POOLING CONFIGURATION
-- ============================================================================

-- Set reasonable connection limits
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- ============================================================================
-- 6. QUERY PERFORMANCE VIEWS
-- ============================================================================

-- View for slow queries
CREATE OR REPLACE VIEW v_slow_queries AS
SELECT 
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- Queries taking > 100ms on average
ORDER BY mean_exec_time DESC;

-- View for table sizes
CREATE OR REPLACE VIEW v_table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- View for index efficiency
CREATE OR REPLACE VIEW v_index_usage AS
SELECT 
    t.tablename,
    i.indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_indexes
JOIN pg_stat_user_indexes idx ON pg_indexes.indexname = idx.indexrelname
JOIN pg_tables t ON pg_indexes.tablename = t.tablename
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- View for unused indexes
CREATE OR REPLACE VIEW v_unused_indexes AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;

-- View for blocking queries
CREATE OR REPLACE VIEW v_blocking_queries AS
SELECT 
    bl.pid AS blocking_pid,
    ka.usename AS blocking_user,
    ka.query AS blocking_query,
    ka.query_start AS blocking_start,
    wd.pid AS waiting_pid,
    wd.usename AS waiting_user,
    wd.query AS waiting_query,
    wd.query_start AS waiting_start
FROM pg_catalog.pg_locks bl
JOIN pg_catalog.pg_stat_activity ka ON bl.pid = ka.pid
JOIN pg_catalog.pg_locks wl ON bl.locktype = wl.locktype
    AND bl.database IS NOT DISTINCT FROM wl.database
    AND bl.relation IS NOT DISTINCT FROM wl.relation
    AND bl.page IS NOT DISTINCT FROM wl.page
    AND bl.tuple IS NOT DISTINCT FROM wl.tuple
    AND bl.virtualxid IS NOT DISTINCT FROM wl.virtualxid
    AND bl.physicalxid IS NOT DISTINCT FROM wl.physicalxid
    AND bl.objid IS NOT DISTINCT FROM wl.objid
    AND bl.objsubid IS NOT DISTINCT FROM wl.objsubid
    AND bl.pid != wl.pid
JOIN pg_catalog.pg_stat_activity wd ON wl.pid = wd.pid
WHERE NOT bl.granted;

-- ============================================================================
-- 7. MAINTENANCE SCHEDULES
-- ============================================================================

-- The following should be scheduled as cron jobs:

-- VACUUM & ANALYZE (nightly)
-- vacuumdb -U postgres -d erp_quty_karunia_production --analyze

-- REINDEX (weekly)
-- reindexdb -U postgres -d erp_quty_karunia_production -j 4

-- FULL BACKUP (daily at 2 AM)
-- pg_dump erp_quty_karunia_production | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

-- ============================================================================
-- 8. MONITORING ALERTS
-- ============================================================================

-- These indexes support monitoring queries:
-- - Transfer bottlenecks: SELECT * FROM transfer_logs WHERE status = 'LOCKED' ORDER BY created_at DESC LIMIT 10;
-- - Line occupancy: SELECT * FROM line_occupancy WHERE is_clear = false;
-- - Slow QC inspections: SELECT * FROM qc_lab_tests WHERE created_at > NOW() - INTERVAL '1 hour' ORDER BY created_at DESC;
-- - Metal detector incidents: SELECT * FROM qc_lab_tests WHERE test_type = 'Metal Detector' AND test_result = 'Fail';

-- ============================================================================
-- 9. VERIFICATION
-- ============================================================================

-- List all created indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Get index statistics
SELECT 
    idx_scan as "Index Scans",
    idx_tup_read as "Tuples Read",
    idx_tup_fetch as "Tuples Fetched",
    indexrelname as "Index Name"
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. All indexes include IF NOT EXISTS to prevent errors on re-runs
-- 2. Partial indexes improve performance on large tables with filtered queries
-- 3. Composite indexes help with multi-column WHERE and JOIN conditions
-- 4. Run ANALYZE after creating indexes for query planner optimization
-- 5. Monitor index usage with v_index_usage and v_unused_indexes views
-- 6. Remember to REINDEX after major data loading operations
-- ============================================================================

