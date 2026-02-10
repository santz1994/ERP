-- ============================================================================
-- MIGRATION 4: PALLET SYSTEM IMPLEMENTATION
-- ============================================================================
-- Date: February 10, 2026
-- Purpose: Add pallet tracking to support fixed packing specifications
-- Business requirement: PO quantities must be pallet multiples
-- Author: IT Fullstack Team
-- ============================================================================

-- ============================================================================
-- STEP 1: ADD PALLET SPECIFICATIONS TO PRODUCTS TABLE
-- ============================================================================
-- Purpose: Store fixed packing specs per article (pcs/carton, cartons/pallet)
-- Example: AFTONSPARV Bear = 60 pcs/carton, 8 cartons/pallet = 480 pcs/pallet

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS pcs_per_carton INTEGER,
ADD COLUMN IF NOT EXISTS cartons_per_pallet INTEGER,
ADD COLUMN IF NOT EXISTS pcs_per_pallet INTEGER GENERATED ALWAYS AS 
    (COALESCE(pcs_per_carton, 0) * COALESCE(cartons_per_pallet, 0)) STORED;

-- Add constraints
ALTER TABLE products 
ADD CONSTRAINT chk_pcs_per_carton_positive 
    CHECK (pcs_per_carton IS NULL OR pcs_per_carton > 0);

ALTER TABLE products 
ADD CONSTRAINT chk_cartons_per_pallet_positive 
    CHECK (cartons_per_pallet IS NULL OR cartons_per_pallet > 0);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_pallet_specs 
    ON products (pcs_per_carton, cartons_per_pallet)
    WHERE pcs_per_carton IS NOT NULL AND cartons_per_pallet IS NOT NULL;

-- Comments
COMMENT ON COLUMN products.pcs_per_carton IS 
    'Fixed number of pieces per carton (e.g., 60 for AFTONSPARV). NULL for non-finished goods.';
COMMENT ON COLUMN products.cartons_per_pallet IS 
    'Fixed number of cartons per pallet (typically 8 from BOM analysis). NULL for non-finished goods.';
COMMENT ON COLUMN products.pcs_per_pallet IS 
    'Auto-computed: pcs_per_carton × cartons_per_pallet (e.g., 480). NULL if either parent field is NULL.';

-- ============================================================================
-- STEP 2: ADD PALLET PLANNING TO PURCHASE ORDERS
-- ============================================================================
-- Purpose: Allow Purchasing to specify target pallets → auto-calculate PCS quantity
-- Business Rule: PO quantity MUST be pallet multiples to prevent partial pallets

ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS target_pallets INTEGER,
ADD COLUMN IF NOT EXISTS expected_cartons INTEGER,
ADD COLUMN IF NOT EXISTS calculated_pcs INTEGER;

-- Add comments
COMMENT ON COLUMN purchase_orders.target_pallets IS 
    'Number of pallets Purchasing wants to produce (input by Purchasing staff)';
COMMENT ON COLUMN purchase_orders.expected_cartons IS 
    'Auto-computed: target_pallets × article.cartons_per_pallet';
COMMENT ON COLUMN purchase_orders.calculated_pcs IS 
    'Auto-computed: target_pallets × article.pcs_per_pallet. Must match article_qty.';

-- Add index for reporting
CREATE INDEX IF NOT EXISTS idx_po_pallet_tracking 
    ON purchase_orders (target_pallets)
    WHERE target_pallets IS NOT NULL;

-- ============================================================================
-- STEP 3: ADD PALLET TRACKING TO WORK ORDERS (PACKING DEPT)
-- ============================================================================
-- Purpose: Track cartons packed and pallets formed during packing operations
-- Business Rule: cartons_packed MUST be multiple of article.cartons_per_pallet

ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS cartons_packed INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS pallets_formed INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS packing_validated BOOLEAN DEFAULT FALSE;

-- Add comments
COMMENT ON COLUMN work_orders.cartons_packed IS 
    'Number of cartons packed (must be multiple of article.cartons_per_pallet)';
COMMENT ON COLUMN work_orders.pallets_formed IS 
    'Number of pallets formed: cartons_packed / article.cartons_per_pallet';
COMMENT ON COLUMN work_orders.packing_validated IS 
    'TRUE if packing quantities validated (no partial cartons/pallets)';

-- Add index for packing dashboard
CREATE INDEX IF NOT EXISTS idx_wo_packing_status 
    ON work_orders (department, packing_validated)
    WHERE department = 'Packing';

-- ============================================================================
-- STEP 4: ADD PALLET TRACKING TO FG WAREHOUSE STOCK
-- ============================================================================
-- Purpose: Display FG stock in "PLT / CTN / PCS" format
-- Business Rule: FG stock should be stored and displayed at pallet level

-- Add computed columns to stock_quants for display
ALTER TABLE stock_quants 
ADD COLUMN IF NOT EXISTS display_pallets INTEGER,
ADD COLUMN IF NOT EXISTS display_cartons INTEGER;

-- Add comments
COMMENT ON COLUMN stock_quants.display_pallets IS 
    'Display: Number of complete pallets (quantity / product.pcs_per_pallet)';
COMMENT ON COLUMN stock_quants.display_cartons IS 
    'Display: Remaining cartons after pallets ((quantity % pcs_per_pallet) / pcs_per_carton)';

-- ============================================================================
-- STEP 5: CREATE PALLET BARCODE TABLE (FOR FG TRACKING)
-- ============================================================================
-- Purpose: Track individual pallet barcodes for FG warehouse receiving
-- Business Rule: Each pallet gets unique barcode PLT-YYYY-XXXXX

CREATE TABLE IF NOT EXISTS pallet_barcodes (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    work_order_id INTEGER REFERENCES work_orders(id) ON DELETE SET NULL,
    
    -- Pallet content
    carton_count INTEGER NOT NULL CHECK (carton_count > 0),
    total_pcs INTEGER NOT NULL CHECK (total_pcs > 0),
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'PACKED' CHECK (status IN ('PACKED', 'RECEIVED', 'SHIPPED')),
    
    -- Warehouse location
    location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    received_at TIMESTAMP WITH TIME ZONE,
    shipped_at TIMESTAMP WITH TIME ZONE,
    
    -- Ensure pallet content matches product specs
    CONSTRAINT chk_pallet_content_valid CHECK (
        -- If product has pallet specs, validate content
        (SELECT pcs_per_pallet FROM products WHERE id = product_id) IS NULL
        OR total_pcs = carton_count * (SELECT pcs_per_carton FROM products WHERE id = product_id)
    )
);

-- Indexes
CREATE INDEX idx_pallet_barcode ON pallet_barcodes (barcode);
CREATE INDEX idx_pallet_product ON pallet_barcodes (product_id);
CREATE INDEX idx_pallet_status ON pallet_barcodes (status);
CREATE INDEX idx_pallet_location ON pallet_barcodes (location_id);

-- Comments
COMMENT ON TABLE pallet_barcodes IS 
    'Individual pallet tracking for FG warehouse. Each pallet has unique barcode.';
COMMENT ON COLUMN pallet_barcodes.barcode IS 
    'Unique pallet barcode (format: PLT-2026-00001)';
COMMENT ON COLUMN pallet_barcodes.carton_count IS 
    'Number of cartons on this pallet (should match product.cartons_per_pallet)';
COMMENT ON COLUMN pallet_barcodes.total_pcs IS 
    'Total pieces on this pallet (should match product.pcs_per_pallet)';

-- ============================================================================
-- STEP 6: ADD VALIDATION VIEWS
-- ============================================================================

-- View: PO Pallet Validation
CREATE OR REPLACE VIEW vw_po_pallet_validation AS
SELECT 
    po.id AS po_id,
    po.po_number,
    po.po_type,
    p.code AS article_code,
    p.name AS article_name,
    p.pcs_per_carton,
    p.cartons_per_pallet,
    p.pcs_per_pallet,
    po.target_pallets,
    po.expected_cartons,
    po.calculated_pcs,
    po.article_qty,
    -- Validation flags
    CASE 
        WHEN po.article_qty = po.calculated_pcs THEN TRUE
        ELSE FALSE
    END AS quantity_matches,
    CASE 
        WHEN p.pcs_per_pallet IS NOT NULL 
             AND po.article_qty % p.pcs_per_pallet = 0 THEN TRUE
        ELSE FALSE
    END AS is_pallet_multiple
FROM purchase_orders po
LEFT JOIN products p ON po.article_id = p.id
WHERE po.po_type IN ('KAIN', 'LABEL')
AND p.type = 'Finish Good';

COMMENT ON VIEW vw_po_pallet_validation IS 
    'Validates PO quantities are pallet multiples. Used by Purchasing UI for validation.';

-- View: Packing Progress with Pallet Tracking
CREATE OR REPLACE VIEW vw_packing_pallet_progress AS
SELECT 
    wo.id AS wo_id,
    wo.spk_number,
    p.code AS article_code,
    p.name AS article_name,
    p.pcs_per_carton,
    p.cartons_per_pallet,
    p.pcs_per_pallet,
    wo.target_qty,
    wo.actual_good_output,
    wo.cartons_packed,
    wo.pallets_formed,
    wo.packing_validated,
    -- Expected vs Actual
    CEIL(wo.target_qty::NUMERIC / p.pcs_per_carton) AS expected_cartons,
    CEIL(wo.target_qty::NUMERIC / p.pcs_per_pallet) AS expected_pallets,
    -- Validation
    CASE 
        WHEN wo.cartons_packed % p.cartons_per_pallet = 0 THEN TRUE
        ELSE FALSE
    END AS is_complete_pallets
FROM work_orders wo
JOIN products p ON wo.product_id = p.id
WHERE wo.department = 'Packing'
AND p.type = 'Finish Good'
AND p.pcs_per_pallet IS NOT NULL;

COMMENT ON VIEW vw_packing_pallet_progress IS 
    'Tracks packing progress with pallet formation validation. Used by Packing dashboard.';

-- View: FG Stock in Pallet/Carton/Pcs Format
CREATE OR REPLACE VIEW vw_fg_stock_pallet_display AS
SELECT 
    sq.id AS stock_id,
    sq.location_id,
    l.name AS location_name,
    p.id AS product_id,
    p.code AS product_code,
    p.name AS product_name,
    p.pcs_per_carton,
    p.cartons_per_pallet,
    p.pcs_per_pallet,
    sq.quantity AS total_pcs,
    -- Display breakdown
    FLOOR(sq.quantity / p.pcs_per_pallet) AS pallets,
    FLOOR((sq.quantity % p.pcs_per_pallet) / p.pcs_per_carton) AS remaining_cartons,
    sq.quantity % p.pcs_per_carton AS loose_pcs,
    -- Formatted display
    CONCAT(
        FLOOR(sq.quantity / p.pcs_per_pallet), ' PLT / ',
        FLOOR((sq.quantity % p.pcs_per_pallet) / p.pcs_per_carton), ' CTN / ',
        sq.quantity % p.pcs_per_carton, ' PCS'
    ) AS display_format
FROM stock_quants sq
JOIN products p ON sq.product_id = p.id
JOIN locations l ON sq.location_id = l.id
WHERE p.type = 'Finish Good'
AND p.pcs_per_pallet IS NOT NULL
AND sq.quantity > 0;

COMMENT ON VIEW vw_fg_stock_pallet_display IS 
    'FG stock displayed in "PLT / CTN / PCS" format for warehouse staff.';

-- ============================================================================
-- STEP 7: UPDATE EXISTING DATA (OPTIONAL - RUN AFTER IMPORTING PACKING DATA)
-- ============================================================================

-- Placeholder: Update products with pallet specs from Excel import
-- This will be populated after running the packing data import script

-- Example update (uncomment after import):
-- UPDATE products SET 
--     pcs_per_carton = 60,
--     cartons_per_pallet = 8
-- WHERE code = 'AFTONSPARV' AND type = 'Finish Good';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- 1. Check products with pallet specs
SELECT 
    code, 
    name, 
    type,
    pcs_per_carton,
    cartons_per_pallet,
    pcs_per_pallet
FROM products 
WHERE pcs_per_pallet IS NOT NULL
ORDER BY code
LIMIT 10;

-- 2. Check PO pallet validation
SELECT * FROM vw_po_pallet_validation 
WHERE NOT quantity_matches OR NOT is_pallet_multiple
LIMIT 10;

-- 3. Check packing progress
SELECT * FROM vw_packing_pallet_progress
WHERE NOT is_complete_pallets
LIMIT 10;

-- 4. Check FG stock display
SELECT * FROM vw_fg_stock_pallet_display
ORDER BY pallets DESC
LIMIT 10;

-- ============================================================================
-- ROLLBACK SCRIPT (IF NEEDED)
-- ============================================================================

/*
-- DROP VIEWS
DROP VIEW IF EXISTS vw_fg_stock_pallet_display;
DROP VIEW IF EXISTS vw_packing_pallet_progress;
DROP VIEW IF EXISTS vw_po_pallet_validation;

-- DROP TABLE
DROP TABLE IF EXISTS pallet_barcodes;

-- REMOVE COLUMNS FROM STOCK_QUANTS
ALTER TABLE stock_quants 
DROP COLUMN IF EXISTS display_pallets,
DROP COLUMN IF EXISTS display_cartons;

-- REMOVE COLUMNS FROM WORK_ORDERS
ALTER TABLE work_orders 
DROP COLUMN IF EXISTS cartons_packed,
DROP COLUMN IF EXISTS pallets_formed,
DROP COLUMN IF EXISTS packing_validated;

-- REMOVE COLUMNS FROM PURCHASE_ORDERS
ALTER TABLE purchase_orders 
DROP COLUMN IF EXISTS target_pallets,
DROP COLUMN IF EXISTS expected_cartons,
DROP COLUMN IF EXISTS calculated_pcs;

-- REMOVE COLUMNS FROM PRODUCTS
ALTER TABLE products 
DROP COLUMN IF EXISTS pcs_per_pallet,
DROP COLUMN IF EXISTS cartons_per_pallet,
DROP COLUMN IF EXISTS pcs_per_carton;
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
