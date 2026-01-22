-- ============================================================================
-- Dashboard Materialized Views - Simplified Version
-- ============================================================================
-- Author: Daniel - IT Developer Senior
-- Date: 2026-01-22
-- ============================================================================

-- ============================================================================
-- 1. Dashboard Statistics Summary
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_stats CASCADE;

CREATE MATERIALIZED VIEW mv_dashboard_stats AS
SELECT
    -- Total Manufacturing Orders (not cancelled)
    (SELECT COUNT(*) FROM manufacturing_orders WHERE state != 'CANCELLED') 
        AS total_mos,
    
    -- Completed today
    (SELECT COUNT(*) FROM manufacturing_orders 
     WHERE state = 'DONE' 
     AND completed_at::date = CURRENT_DATE) 
        AS completed_today,
    
    -- Pending QC inspection
    (SELECT COUNT(*) FROM qc_inspections 
     WHERE status != 'PASS') 
        AS pending_qc,
    
    -- Critical alerts (audit logs last 24h)
    (SELECT COUNT(*) FROM audit_logs 
     WHERE timestamp >= NOW() - INTERVAL '24 hours') 
        AS critical_alerts,
    
    -- Metadata
    NOW() AS refreshed_at;


-- ============================================================================
-- 2. Production Department Status
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_production_dept_status CASCADE;

CREATE MATERIALIZED VIEW mv_production_dept_status AS
SELECT
    department AS dept,
    COUNT(*) AS total_jobs,
    SUM(CASE WHEN status = 'FINISHED' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'RUNNING' THEN 1 ELSE 0 END) AS in_progress,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending,
    COALESCE(AVG(
        CASE 
            WHEN status = 'FINISHED' THEN 100 
            WHEN status = 'RUNNING' THEN 50 
            ELSE 0 
        END
    ), 0) AS avg_progress,
    CASE
        WHEN SUM(CASE WHEN status = 'RUNNING' THEN 1 ELSE 0 END) > 0 
            THEN 'Running'
        WHEN SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) > 0 
            THEN 'Pending'
        ELSE 'Idle'
    END AS status,
    NOW() AS refreshed_at
FROM work_orders
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY department;


-- ============================================================================
-- 3. QC Pass Rate by Department
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_qc_pass_rate CASCADE;

CREATE MATERIALIZED VIEW mv_qc_pass_rate AS
WITH qc_stats AS (
    SELECT
        wo.department,
        COUNT(*) AS total_inspections,
        SUM(CASE WHEN qi.status = 'PASS' THEN 1 ELSE 0 END) AS passed,
        SUM(CASE WHEN qi.status = 'FAIL' THEN 1 ELSE 0 END) AS failed
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
WHERE p.type IN ('RAW_MATERIAL', 'WIP')
GROUP BY p.id, p.code, p.name, p.type, p.min_stock;
