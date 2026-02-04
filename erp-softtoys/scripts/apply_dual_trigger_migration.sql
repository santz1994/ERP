-- Manual SQL Migration for Dual Trigger & Flexible Target System
-- Run this directly in psql or through Python script
-- Date: 2026-02-04
-- Author: IT Developer Expert

-- ============================================================================
-- 1. MANUFACTURING ORDERS - Add Dual Trigger Fields
-- ============================================================================

-- Check if columns already exist first
DO $$ 
BEGIN
    -- Add po_fabric_id
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='manufacturing_orders' AND column_name='po_fabric_id') THEN
        ALTER TABLE manufacturing_orders 
        ADD COLUMN po_fabric_id INTEGER REFERENCES purchase_orders(id);
        
        CREATE INDEX ix_manufacturing_orders_po_fabric_id ON manufacturing_orders(po_fabric_id);
        
        RAISE NOTICE '✅ Added po_fabric_id to manufacturing_orders';
    ELSE
        RAISE NOTICE '⚠️  po_fabric_id already exists';
    END IF;
    
    -- Add po_label_id
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='manufacturing_orders' AND column_name='po_label_id') THEN
        ALTER TABLE manufacturing_orders 
        ADD COLUMN po_label_id INTEGER REFERENCES purchase_orders(id);
        
        CREATE INDEX ix_manufacturing_orders_po_label_id ON manufacturing_orders(po_label_id);
        
        RAISE NOTICE '✅ Added po_label_id to manufacturing_orders';
    ELSE
        RAISE NOTICE '⚠️  po_label_id already exists';
    END IF;
    
    -- Add trigger_mode
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='manufacturing_orders' AND column_name='trigger_mode') THEN
        ALTER TABLE manufacturing_orders 
        ADD COLUMN trigger_mode VARCHAR(20) NOT NULL DEFAULT 'PARTIAL';
        
        CREATE INDEX ix_manufacturing_orders_trigger_mode ON manufacturing_orders(trigger_mode);
        
        COMMENT ON COLUMN manufacturing_orders.po_fabric_id IS 
            'PO for fabric materials (TRIGGER 1: enables Cutting/Embroidery)';
        COMMENT ON COLUMN manufacturing_orders.po_label_id IS 
            'PO for labels/tags (TRIGGER 2: enables all departments)';
        COMMENT ON COLUMN manufacturing_orders.trigger_mode IS 
            'Production release mode: PARTIAL (fabric only) or RELEASED (fabric+label)';
        
        RAISE NOTICE '✅ Added trigger_mode to manufacturing_orders';
    ELSE
        RAISE NOTICE '⚠️  trigger_mode already exists';
    END IF;
END $$;

-- ============================================================================
-- 2. SPK - Add Flexible Target Fields
-- ============================================================================

DO $$ 
BEGIN
    -- Add buffer_percentage
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='spks' AND column_name='buffer_percentage') THEN
        ALTER TABLE spks 
        ADD COLUMN buffer_percentage DECIMAL(5,2) NOT NULL DEFAULT 0;
        
        COMMENT ON COLUMN spks.buffer_percentage IS 
            'Department buffer % (10% Cutting, 6.7% Sewing, etc.)';
        
        RAISE NOTICE '✅ Added buffer_percentage to spks';
    ELSE
        RAISE NOTICE '⚠️  buffer_percentage already exists';
    END IF;
    
    -- Add good_qty
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='spks' AND column_name='good_qty') THEN
        ALTER TABLE spks 
        ADD COLUMN good_qty INTEGER NOT NULL DEFAULT 0;
        
        COMMENT ON COLUMN spks.good_qty IS 'Good output produced';
        
        RAISE NOTICE '✅ Added good_qty to spks';
    ELSE
        RAISE NOTICE '⚠️  good_qty already exists';
    END IF;
    
    -- Add defect_qty
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='spks' AND column_name='defect_qty') THEN
        ALTER TABLE spks 
        ADD COLUMN defect_qty INTEGER NOT NULL DEFAULT 0;
        
        COMMENT ON COLUMN spks.defect_qty IS 'Defect/reject output';
        
        RAISE NOTICE '✅ Added defect_qty to spks';
    ELSE
        RAISE NOTICE '⚠️  defect_qty already exists';
    END IF;
    
    -- Add rework_qty
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='spks' AND column_name='rework_qty') THEN
        ALTER TABLE spks 
        ADD COLUMN rework_qty INTEGER NOT NULL DEFAULT 0;
        
        COMMENT ON COLUMN spks.rework_qty IS 'Sent to rework';
        
        RAISE NOTICE '✅ Added rework_qty to spks';
    ELSE
        RAISE NOTICE '⚠️  rework_qty already exists';
    END IF;
    
    -- Update existing column comments
    COMMENT ON COLUMN spks.original_qty IS 'Base quantity from MO';
    COMMENT ON COLUMN spks.target_qty IS 'Target with buffer (original × buffer)';
    COMMENT ON COLUMN spks.produced_qty IS 'Total produced (good + defect)';
END $$;

-- ============================================================================
-- 3. WORK ORDERS - Update Column Comments (computed properties in Python model)
-- ============================================================================

COMMENT ON COLUMN work_orders.input_qty IS 'Material received as input';
COMMENT ON COLUMN work_orders.output_qty IS 'Good output produced (also aliased as good_qty, actual_qty)';
COMMENT ON COLUMN work_orders.reject_qty IS 'Defective/rejected units (also aliased as defect_qty)';

-- ============================================================================
-- 4. VERIFY CHANGES
-- ============================================================================

DO $$ 
DECLARE
    mo_cols INTEGER;
    spk_cols INTEGER;
BEGIN
    SELECT COUNT(*) INTO mo_cols 
    FROM information_schema.columns 
    WHERE table_name='manufacturing_orders' 
    AND column_name IN ('po_fabric_id', 'po_label_id', 'trigger_mode');
    
    SELECT COUNT(*) INTO spk_cols 
    FROM information_schema.columns 
    WHERE table_name='spks' 
    AND column_name IN ('buffer_percentage', 'good_qty', 'defect_qty', 'rework_qty');
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '🎉 MIGRATION COMPLETE!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Manufacturing Orders: % / 3 dual trigger fields', mo_cols;
    RAISE NOTICE 'SPKs: % / 4 flexible target fields', spk_cols;
    RAISE NOTICE 'Work Orders: Comments updated (computed properties in model)';
    RAISE NOTICE '';
    
    IF mo_cols = 3 AND spk_cols = 4 THEN
        RAISE NOTICE '✅ ALL CHANGES APPLIED SUCCESSFULLY!';
    ELSE
        RAISE WARNING '⚠️  Some columns may already exist - check details above';
    END IF;
END $$;
