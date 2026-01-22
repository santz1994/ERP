-- ============================================================================
-- Dashboard Materialized Views - Fixed for Actual Schema
-- ============================================================================
-- Author: Daniel - IT Developer Senior
-- Date: 2026-01-22
-- Purpose: Create materialized views with correct table names
-- ============================================================================

-- ============================================================================
-- 1. Dashboard Statistics Summary
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_stats CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_stats AS
SELECT
    -- Total Manufacturing Orders (not cancelled)
    (SELECT COUNT(*) FROM manufacturing_orders WHERE state != 'Cancelled') 
        AS total_mos,
    
    -- Completed today
    (SELECT COUNT(*) FROM manufacturing_orders 
     WHERE state = 'Done' 
     AND completed_at::date = CURRENT_DATE) 
        AS completed_today,
    
    -- Pending QC inspection (using actual table name)
    (SELECT COUNT(*) FROM qc_inspections 
     WHERE status = 'pending') 
        AS pending_qc,
    
    -- Critical alerts (audit logs with high severity)
    (SELECT COUNT(*) FROM audit_logs 
     WHERE created_at >= NOW() - INTERVAL '24 hours') 
        AS critical_alerts,
    
    -- Metadata
    NOW() AS refreshed_at;

-- No unique index needed for simple single-row view
COMMENT ON MATERIALIZED VIEW mv_dashboard_stats IS 
'Dashboard top-level statistics - refresh every 5 minutes';


-- ============================================================================
-- 2. Production Department Status (using work_orders table)
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_production_dept_status CASCADE;

CREATE MATERIALIZED VIEW mv_production_dept_status AS
SELECT
    department AS dept,
    COUNT(*) AS total_jobs,
    SUM(CASE WHEN status = 'Finished' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'Running' THEN 1 ELSE 0 END) AS in_progress,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
    COALESCE(AVG(
        CASE 
            WHEN status = 'Finished' THEN 100 
            WHEN status = 'Running' THEN 50 
            ELSE 0 
        END
    ), 0) AS avg_progress,
    CASE
        WHEN SUM(CASE WHEN status = 'Running' THEN 1 ELSE 0 END) > 0 
            THEN 'Running'
        WHEN SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) > 0 
            THEN 'Pending'
        ELSE 'Idle'
    END AS status,
    NOW() AS refreshed_at
FROM work_orders
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY department;

CREATE INDEX idx_mv_production_dept_status_dept 
ON mv_production_dept_status(dept);

COMMENT ON MATERIALIZED VIEW mv_production_dept_status IS 
'Production status by department - refresh every 5 minutes';


-- ============================================================================
-- 3. QC Pass Rate by Department
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_qc_pass_rate CASCADE;

CREATE MATERIALIZED VIEW mv_qc_pass_rate AS
WITH qc_stats AS (
    SELECT
        wo.department,
        COUNT(*) AS total_inspections,
        SUM(CASE WHEN qi.status = 'pass' THEN 1 ELSE 0 END) AS passed,
        SUM(CASE WHEN qi.status = 'fail' THEN 1 ELSE 0 END) AS failed
    FROM qc_inspections qi
    JOIN work_orders wo ON qi.work_order_id = wo.id
    WHERE qi.created_at >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY wo.department
)
SELECT
    department AS dept,
    total_inspections,
    passed,
    failed,
    CASE 
        WHEN total_inspections > 0 
        THEN ROUND((passed::numeric / total_inspections * 100), 2)
        ELSE 0
    END AS pass_rate,
    NOW() AS refreshed_at
FROM qc_stats;

CREATE INDEX idx_mv_qc_pass_rate_dept ON mv_qc_pass_rate(dept);

COMMENT ON MATERIALIZED VIEW mv_qc_pass_rate IS 
'QC pass rate by department (last 7 days) - refresh every 5 minutes';


-- ============================================================================
-- 4. Inventory Status
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_inventory_status CASCADE;

CREATE MATERIALIZED VIEW mv_inventory_status AS
SELECT
    p.id AS product_id,
    p.code AS product_code,
    p.name AS product_name,
    p.type AS product_type,
    COALESCE(SUM(sq.qty_on_hand), 0) AS qty_on_hand,
    COALESCE(SUM(sq.qty_reserved), 0) AS qty_reserved,
    COALESCE(SUM(sq.qty_on_hand - sq.qty_reserved), 0) AS qty_available,
    p.min_stock,
    CASE
        WHEN COALESCE(SUM(sq.qty_on_hand - sq.qty_reserved), 0) <= p.min_stock 
        THEN 'Low Stock'
        WHEN COALESCE(SUM(sq.qty_on_hand - sq.qty_reserved), 0) <= p.min_stock * 1.2 
        THEN 'Warning'
        ELSE 'OK'
    END AS stock_status,
    NOW() AS refreshed_at
FROM products p
LEFT JOIN stock_quants sq ON sq.product_id = p.id
WHERE p.type IN ('Raw Material', 'WIP')
GROUP BY p.id, p.code, p.name, p.type, p.min_stock;

CREATE INDEX idx_mv_inventory_status_product ON mv_inventory_status(product_id);
CREATE INDEX idx_mv_inventory_status_status ON mv_inventory_status(stock_status);

COMMENT ON MATERIALIZED VIEW mv_inventory_status IS 
'Inventory levels and stock warnings - refresh every 5 minutes';


-- ============================================================================
-- Refresh Function (can be called from cron or application)
-- ============================================================================
CREATE OR REPLACE FUNCTION refresh_dashboard_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_dashboard_stats;
    REFRESH MATERIALIZED VIEW mv_production_dept_status;
    REFRESH MATERIALIZED VIEW mv_qc_pass_rate;
    REFRESH MATERIALIZED VIEW mv_inventory_status;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_dashboard_views() IS 
'Refresh all dashboard materialized views at once';


-- ============================================================================
-- Initial Data Population
-- ============================================================================
SELECT refresh_dashboard_views();

-- Verify creation
SELECT 'mv_dashboard_stats' AS view_name, COUNT(*) AS rows FROM mv_dashboard_stats
UNION ALL
SELECT 'mv_production_dept_status', COUNT(*) FROM mv_production_dept_status
UNION ALL
SELECT 'mv_qc_pass_rate', COUNT(*) FROM mv_qc_pass_rate
UNION ALL
SELECT 'mv_inventory_status', COUNT(*) FROM mv_inventory_status;

-- Success message
SELECT 'SUCCESS: All materialized views created and populated' AS result;
